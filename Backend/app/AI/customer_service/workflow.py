import os
import re
import time
from typing import List

from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
import tiktoken
from app.models.company_information.company_model import CreateCompanyInformation
from app.AI.customer_service.models import (
    AgentState,
    StructuredOutputGenerateQuery,
    StructuredOutputIdentifyNextStep,
    StructuredOutputTrustLevelCheck,
    StructuredOutputValidationAgent,
    create_validation_agent_model,
)
from app.utils.logger import get_logger
from app.AI.customer_service.prompts import AgentPromptControl
from app.AI.customer_service.tools import AgentTools
from app.AI.utils.dataset import get_dataset
from app.AI.utils.history import get_history_messages


class Workflow:
    def __init__(
        self,
        base_prompt:str,
        tone:str,
        tools,
        available_databases: List[str],
        detail_data: str,
        company_information: CreateCompanyInformation,
        directory_path: str = None,
        long_memory: bool = False,
        short_memory: bool = False,
        **kwargs,
    ):
        self.base_prompt = base_prompt
        self.tone = tone
        self.available_databases = available_databases
        self.detail_data = detail_data
        self.directory_path = directory_path
        self.kwargs = kwargs
        self.llm_for_reasoning = ChatOpenAI(model="gpt-4o-mini")
        self.llm_for_explanation = ChatOpenAI(model="gpt-4o-mini")
        # self.tools = AgentTools(self.chromadb_path, self.collection_name)
        self.tools = tools
        self.next_agent_step = "end"
        self.retry = 0
        self.memory_provider = os.environ.get("MEMORY_PROVIDER")
        self.provider_host = os.environ.get("PROVIDER_HOST")
        self.provider_port = os.environ.get("PROVIDER_PORT")
        self.short_memory = short_memory
        self.long_memory = long_memory
        self.checkpointer = MemorySaver()
        self.prompts = AgentPromptControl(
            is_include_memory=long_memory,
            memory_provider=self.memory_provider,
            provider_host=self.provider_host,
            provider_port=self.provider_port,
        )
        self.company_information = company_information

        self.validation_agent_model = create_validation_agent_model(available_databases)
        self.logger = get_logger(__name__)
        
        # Initialize tokenizer for token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o-mini")
        except KeyError:
            # Fallback to cl100k_base encoding if model not found
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

        self.build = self._build_workflow()

    def _validate_user_input(self, user_message: str) -> bool:
        """Validate user input for security and format"""
        try:
            if not user_message or len(user_message.strip()) == 0:
                self.logger.warning("Empty user message received")
                return False

            if len(user_message) > 1000:
                self.logger.warning(
                    f"User message too long: {len(user_message)} characters"
                )
                return False

            # Check for potentially malicious SQL injection patterns
            malicious_patterns = [
                r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE)\b",
                r"--",
                r"/\*",
                r"\*/",
                r"xp_",
                r"sp_",
            ]
            for pattern in malicious_patterns:
                if re.search(pattern, user_message.upper()):
                    self.logger.warning(
                        f"Potentially malicious input detected: {pattern}"
                    )
                    return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating user input: {str(e)}")
            return False

    def _retry_with_backoff(self, func, max_retries: int = 3, base_delay: float = 1.0):
        """Retry function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(
                        f"Max retries ({max_retries}) exceeded. Last error: {str(e)}"
                    )
                    raise e

                delay = base_delay * (2**attempt)
                self.logger.warning(
                    f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s..."
                )
                time.sleep(delay)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text using tiktoken"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception as e:
            self.logger.warning(f"Error estimating tokens: {str(e)}")
            # Fallback: rough estimation (1 token ≈ 4 characters)
            return len(text) // 4

    def _estimate_structured_output_tokens(self, prompt: str, response_content: str = "") -> int:
        """Estimate tokens for structured output calls"""
        try:
            # Estimate input tokens from prompt
            input_tokens = self._estimate_tokens(prompt)
            
            # Estimate output tokens from response content
            output_tokens = self._estimate_tokens(response_content) if response_content else 50
            
            # Add overhead for structured output formatting
            overhead_tokens = 20
            
            return input_tokens + output_tokens + overhead_tokens
        except Exception as e:
            self.logger.warning(f"Error estimating structured output tokens: {str(e)}")
            return 100  # Default fallback

    def _handle_error(
        self, error_type: str, error_message: str, user_message: str = ""
    ) -> str:
        """Handle different types of errors with appropriate user messages"""
        self.logger.error(f"{error_type}: {error_message}")

        error_responses = {
            "database_error": "Maaf, sistem database sedang mengalami gangguan. Silakan coba lagi nanti.",
            "ai_service_error": "Layanan AI sedang sibuk. Mohon tunggu sebentar dan coba lagi.",
            "file_not_found": "Data yang diminta tidak ditemukan. Silakan coba dengan pertanyaan lain.",
            "validation_error": "Terjadi kesalahan dalam memproses permintaan Anda. Silakan coba lagi.",
            "timeout_error": "Permintaan Anda membutuhkan waktu lebih lama dari biasanya. Silakan coba lagi.",
            "rate_limit_error": "Terlalu banyak permintaan. Mohon tunggu sebentar sebelum mencoba lagi.",
            "general_error": "Terjadi kesalahan teknis. Tim kami akan segera memperbaikinya.",
        }

        return error_responses.get(error_type, error_responses["general_error"])

    def _build_workflow(self):
        graph = StateGraph(AgentState)
        graph.add_node("main_agent", self._main_agent)
        graph.add_node("get_document", ToolNode(tools=[self.tools.get_document]))
        graph.add_node("validation_agent", self._validation_agent)
        graph.add_node("agent_identify_next_step", self._agent_identify_next_step)
        graph.add_node("agent_generate_query", self._agent_generate_query)
        graph.add_node("agent_answer_query", self._agent_answer_query)
        graph.add_node("trust_level_check", self._trust_level_check)
        graph.add_edge(START, "trust_level_check")
        graph.add_conditional_edges(
            "trust_level_check",
            self._trust_level_router,
            {"main_agent": "main_agent", "end": END},
        )
        graph.add_conditional_edges(
            "main_agent",
            self._should_continue,
            {"tool_call": "get_document", "end": END},
        )
        graph.add_edge("get_document", "validation_agent")
        # Buat routing dinamis berdasarkan database yang tersedia
        routing_options = {}
        for db in self.available_databases:
            routing_options[f"check_{db}_database"] = "agent_identify_next_step"
        routing_options["end"] = END

        graph.add_conditional_edges(
            "validation_agent",
            self._next_step,
            routing_options,
        )
        graph.add_edge("agent_identify_next_step", "agent_generate_query")
        graph.add_conditional_edges(
            "agent_generate_query",
            self._query_again,
            {"agent_generate_query": "agent_generate_query", "end": "agent_answer_query"},
        )
        graph.add_edge("agent_answer_query", END)
        # graph.add_edge(START, "main_agent")
        # graph.add_edge("main_agent", END)
        return graph.compile(checkpointer=self.checkpointer)

    def _trust_level_check(self, state: AgentState):
        print("\n" + "="*60)
        print("🔍 TRUST LEVEL CHECK")
        print("="*60)

        history_messages = get_history_messages(state.messages)
        if len(history_messages) >8:
            prompt = self.prompts.trust_level_check(history_messages)
            llm = self.llm_for_reasoning.with_structured_output(
                StructuredOutputTrustLevelCheck
            )
            response = llm.invoke(prompt)
            
            # Estimate tokens for structured output
            estimated_tokens = self._estimate_structured_output_tokens(
                str(prompt), 
                f"trust_level: {response.trust_level}, message: {response.message}, problem: {response.problem}"
            )
            
            print(f"📊 Trust Level: {response.trust_level}%")
            print(f"💬 Message: {response.message}")
            print(f"🎯 Problem: {response.problem}")
            print(f"🔢 Estimated Tokens: {estimated_tokens}")
            print("="*60)
            return {
                "trust_level": response.trust_level,
                "message_for_user": response.message,
                "user_problem": response.problem,
                "total_token": state.total_token + estimated_tokens,
            }
        print("📊 Trust Level: 100% (Default - New User)")
        print("=" * 60)
        return {
            "trust_level": 100,
            "total_token": state.total_token,
        }

    def _trust_level_router(self, state: AgentState):
        if state.trust_level < 50:
            return "end"
        return "main_agent"

    def _formatted_message(self, messages):
        formatted = []
        for message in messages:
            data = {}
            if isinstance(message, HumanMessage):
                data["role"] = "user"
                data["content"] = message.content
                formatted.append(data)
            elif isinstance(message, AIMessage):
                data["role"] = "assistant"
                data["content"] = message.content
                formatted.append(data)
        return formatted

    def _get_all_previous_messages(self, messages):
        all_previous_messages = []
        if self.short_memory:
            all_previous_messages = messages
        if len(all_previous_messages) > 6:
            all_previous_messages = all_previous_messages[
                6 : len(all_previous_messages)
            ]
        return all_previous_messages

    def _main_agent(self, state: AgentState):
        try:
            self.logger.info(
                f"Main agent processing user message: {state.user_message[:50]}..."
            )
            print(f"detail_data: {self.detail_data}")
            print(f"available_databases: {self.available_databases}")
            print(f"kwargs: {self.kwargs}")
            # Validate user input
            if not self._validate_user_input(state.user_message):
                error_msg = self._handle_error(
                    "validation_error", "Invalid user input", state.user_message
                )
                return {
                    "messages": state.messages
                    + [HumanMessage(content=state.user_message)]
                    + [AIMessage(content=error_msg)],
                    "response": error_msg,
                    "total_token": state.total_token,
                }

            all_previous_messages = self._get_all_previous_messages(state.messages)
            print(f"available_databases: {self.available_databases}")
            print(f"detail_data: {self.detail_data}")
            print(f"kwargs: {self.kwargs}")

            # Generate prompt and invoke LLM with retry mechanism
            def invoke_llm():
                prompt = self.prompts.main_agent(state.user_message, self.base_prompt, self.tone, self.company_information)
                print(f"prompt: {prompt}")
                messages = [prompt[0]] + all_previous_messages + [prompt[1]]
                llm = self.llm_for_reasoning.bind_tools([self.tools.get_document])
                return llm.invoke(messages)

            response = self._retry_with_backoff(invoke_llm, max_retries=3)

            if self.prompts.is_include_memory and not response.tool_calls:
                message = [
                    HumanMessage(content=state.user_message),
                    AIMessage(content=response.content),
                ]
                formatted_message = self._formatted_message(message)
                if self.prompts.memory_id:
                    self.prompts.memory.add_context(
                        formatted_message, self.prompts.memory_id
                    )

            self.logger.info("Main agent response generated successfully")
            return {
                "messages": state.messages
                + [HumanMessage(content=state.user_message)]
                + [response],
                "response": response.content,
                "total_token": state.total_token
                + response.usage_metadata.get("total_tokens", 0),
            }

        except Exception as e:
            error_msg = self._handle_error(
                "ai_service_error", str(e), state.user_message
            )
            self.logger.error(f"Error in main agent: {str(e)}", exc_info=True)
            return {
                "messages": state.messages
                + [HumanMessage(content=state.user_message)]
                + [AIMessage(content=error_msg)],
                "response": error_msg,
                "total_token": state.total_token,
            }

    def _should_continue(self, state: AgentState):
        last_message = state.messages[-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            return "tool_call"
        return "end"

    def _validation_agent(self, state: AgentState):
        try:
            self.logger.info("Validation agent processing tool message")

            if not state.messages:
                self.logger.error("No messages found in state")
                return {
                    "can_answer": False,
                    "reason": "No messages available for validation",
                    "next_step": "end",
                    "total_token": state.total_token,
                }

            tool_message = str(state.messages[-1].content) if state.messages[-1].content else ""
            self.logger.info(f"Tool message: {tool_message[:100]}...")

            # Invoke LLM with retry mechanism
            def invoke_validation():
                llm = self.llm_for_reasoning.with_structured_output(
                    self.validation_agent_model
                )
                prompts = self.prompts.agent_validation(
                    state.user_message, tool_message, self.detail_data, **self.kwargs
                )
                return llm.invoke(prompts)

            response = self._retry_with_backoff(invoke_validation, max_retries=2)
            print(f"response: {response}")
            # Estimate tokens for structured output
            prompts = self.prompts.agent_validation(state.user_message, tool_message, self.detail_data, **self.kwargs)
            estimated_tokens = self._estimate_structured_output_tokens(
                str(prompts),
                f"can_answer: {response.can_answer}, reasoning: {response.reasoning}, next_step: {response.next_step}"
            )

            self.logger.info(
                f"Validation result: can_answer={response.can_answer}, next_step={response.next_step}, tokens={estimated_tokens}"
            )
            return {
                "can_answer": response.can_answer,
                "reason": response.reasoning,
                "response":tool_message,
                "next_step": response.next_step,
                "total_token": state.total_token + estimated_tokens,
            }

        except Exception as e:
            self.logger.error(f"Error in validation agent: {str(e)}", exc_info=True)
            return {
                "can_answer": False,
                "reason": f"Validation error: {str(e)}",
                "next_step": "end",
                "total_token": state.total_token,
            }

    def _next_step(self, state: AgentState):
        if state.can_answer or state.next_step == "end":
            return "end"
        print(f"state.next_step: {state.next_step}")
        self.next_agent_step = state.next_step
        return state.next_step

    def _agent_identify_next_step(self, state: AgentState):
        print("\n" + "="*60)
        print("🧠 AGENT IDENTIFY NEXT STEP")
        print("="*60)

        prompt = self.prompts.agent_identify_next_step(
            state.user_message, self.detail_data, state.reason
        )
        llm = self.llm_for_reasoning.with_structured_output(
            StructuredOutputIdentifyNextStep
        )
        response = llm.invoke(prompt)
        
        # Estimate tokens for structured output
        estimated_tokens = self._estimate_structured_output_tokens(
            str(prompt),
            f"problem: {response.problem}, problem_solving: {response.problem_solving}"
        )
        
        print(f"🎯 Problem: {response.problem}")
        print(f"💡 Problem Solving: {response.problem_solving}")
        print(f"🔢 Estimated Tokens: {estimated_tokens}")
        print("="*60)
        return {
            "problem": response.problem,
            "problem_solving": response.problem_solving,
            "total_token": state.total_token + estimated_tokens,
        }

    def _agent_generate_query(self, state: AgentState):
        try:
            self.logger.info(f"Generating query for problem: {state.problem[:50]}...")

            if self.retry > 0:
                problem_solving = state.next_query_desc or ""
                self.logger.info(f"Retry #{self.retry} - using next query description")
            else:
                problem_solving = state.problem_solving or ""

            # Generate query with retry mechanism
            def generate_query():
                prompt = self.prompts.agent_generate_query(
                    state.problem, problem_solving, self.detail_data
                )
                llm = self.llm_for_reasoning.with_structured_output(
                    StructuredOutputGenerateQuery
                )
                return llm.invoke(prompt)

            response = self._retry_with_backoff(generate_query, max_retries=2)
            print(f"response: {response}")
            # Estimate tokens for structured output
            prompt = self.prompts.agent_generate_query(state.problem, problem_solving, self.detail_data)
            estimated_tokens = self._estimate_structured_output_tokens(
                str(prompt),
                f"query: {response.query}, db_name: {response.db_name}, file_path: {response.file_path}, query_again: {response.query_again}, next_query_desc: {response.next_query_desc}"
            )

            self.logger.info(f"Generated query: {response.query[:100]}...")
            self.logger.info(f"Target database: {response.db_name}")
            self.logger.info(f"Estimated tokens: {estimated_tokens}")

            # Execute database query with comprehensive error handling
            try:
                # Use the directory_path from agent initialization for dataset location
                db_path = os.path.join(self.directory_path, f"{response.db_name}.db")
                result_df = get_dataset(
                    response.file_path,
                    db_path,
                    response.query,
                    response.db_name,
                )

                if result_df is None or result_df.empty:
                    self.logger.warning("Query returned empty result")
                    result_str = "Tidak ada data yang ditemukan untuk query ini."
                else:
                    result_str = result_df.to_string(index=True)
                    self.logger.info(
                        f"Query executed successfully, returned {len(result_df)} rows"
                    )

            except FileNotFoundError as e:
                self.logger.error(f"Database file not found: {str(e)}")
                error_msg = self._handle_error("file_not_found", str(e))
                return {
                    "query": response.query,
                    "result": f"{state.result}\n{error_msg}",
                    "query_again": False,
                    "next_query_desc": "",
                    "total_token": state.total_token,
                }
            except Exception as e:
                self.logger.error(f"Database query error: {str(e)}")
                error_msg = self._handle_error("database_error", str(e))
                return {
                    "query": response.query,
                    "result": f"{state.result}\n{error_msg}",
                    "query_again": False,
                    "next_query_desc": "",
                    "total_token": state.total_token,
                }

            return {
                "query": response.query,
                "result": f"{state.result}\n{result_str}",
                "query_again": response.query_again,
                "next_query_desc": response.next_query_desc,
                "total_token": state.total_token + estimated_tokens,
            }

        except Exception as e:
            self.logger.error(f"Error in query generation: {str(e)}", exc_info=True)
            error_msg = self._handle_error("ai_service_error", str(e))
            return {
                "query": "",
                "result": f"{state.result}\n{error_msg}",
                "query_again": False,
                "next_query_desc": "",
                "total_token": state.total_token,
            }

    def _query_again(self, state: AgentState):
        print("\n" + "="*60)
        print("🔄 QUERY AGAIN CHECK")
        print("="*60)

        if self.retry > 5:
            print("❌ Max retry limit reached (5)")
            print("="*60)
            return "end"
        if state.query_again:
            print(f"✅ Query again requested - Retry #{self.retry + 1}")
            self.retry += 1
            print("=" * 60)
            return "agent_generate_query"
        print("✅ No more queries needed")
        print("=" * 60)
        return "end"

    def _agent_answer_query(self, state: AgentState):
        try:
            self.logger.info("Generating final answer for user")

            if not state.result or state.result.strip() == "":
                self.logger.warning("No query results available for answer generation")
                error_msg = self._handle_error(
                    "validation_error", "No data available to generate answer"
                )
                return {
                    "messages": state.messages + [AIMessage(content=error_msg)],
                    "response": error_msg,
                }

            # Generate final answer with retry mechanism
            def generate_answer():
                prompt = self.prompts.agent_answer_query(
                    state.user_message, state.result, state.problem
                )
                llm = self.llm_for_explanation
                return llm.invoke(prompt)

            response = self._retry_with_backoff(generate_answer, max_retries=2)

            if self.prompts.is_include_memory:
                message = [
                    HumanMessage(content=state.user_message),
                    AIMessage(content=response.content),
                ]
                formatted_message = self._formatted_message(message)
                if self.prompts.memory_id:
                    self.prompts.memory.add_context(
                        formatted_message, self.prompts.memory_id
                    )

            self.logger.info("Final answer generated successfully")
            return {
                "messages": state.messages + [response],
                "response": response.content,
                "total_token": state.total_token
                + response.usage_metadata.get("total_tokens", 0),
            }

        except Exception as e:
            self.logger.error(f"Error in answer generation: {str(e)}", exc_info=True)
            error_msg = self._handle_error("ai_service_error", str(e))
            return {
                "messages": state.messages + [AIMessage(content=error_msg)],
                "response": error_msg,
            }

    def run(self, state: AgentState, thread_id: str):
        return self.build.invoke(
            state,
            config={"configurable": {"thread_id": thread_id}},
        )


# if __name__ == "__main__":
#     workflow = Workflow("data", "my_collections")
#     result = workflow.run(state={"user_message": "apa itu visi perusahaan"})
#     print(result)
