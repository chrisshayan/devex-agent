"""
Morning Brief Workflow - Real LangGraph Implementation
Advanced ambient agent workflow following LangChain Academy patterns
"""

from typing import Dict, Any, List, Annotated, Optional, TypedDict
from datetime import datetime, timedelta
import logging
import json

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from .code_analyzer import CodeAnalyzer
from .enhanced_code_analyzer import run_enhanced_analysis
from ..config.settings import get_settings

logger = logging.getLogger(__name__)

class MorningBriefState(TypedDict, total=False):
    """State for the morning brief workflow"""
    developer_id: str
    events: List[Dict[str, Any]]
    context: Dict[str, Any]
    event_categories: Dict[str, List[Dict[str, Any]]]
    event_stats: Dict[str, Any]
    code_analysis: Dict[str, Any]
    build_analysis: Dict[str, Any]
    pattern_analysis: Dict[str, Any]
    knowledge_graph_insights: Dict[str, Any]  # NEW: KG insights
    critical_insights: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    morning_brief: Dict[str, Any]
    messages: Annotated[List[BaseMessage], add_messages]

class MorningBriefWorkflow:
    """
    LangGraph workflow for generating sophisticated morning briefs
    
    Workflow nodes:
    1. analyze_events -> Categorize and preprocess events
    2. code_analysis -> Deep code analysis using LLM + Tree-sitter
    3. knowledge_graph_analysis -> Get insights from Knowledge Graph
    4. pattern_detection -> Identify patterns and anomalies
    5. generate_insights -> Create actionable insights
    6. compile_brief -> Generate final morning brief
    """
    
    def __init__(self, openai_api_key: Optional[str] = None, knowledge_graph_service=None):
        self.settings = get_settings()
        self.code_analyzer = CodeAnalyzer(openai_api_key)
        self.knowledge_graph_service = knowledge_graph_service  # NEW: KG service
        # Temporarily disable LLM to avoid API quota issues
        self.llm = None
        
        if openai_api_key:
            self.llm = ChatOpenAI(
                api_key=openai_api_key,
                model=self.settings.llm_model,
                temperature=self.settings.llm_temperature
            )
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(MorningBriefState)
        
        # Add nodes (renamed to avoid conflicts with state keys)
        workflow.add_node("analyze_events", self.analyze_events_node)
        workflow.add_node("analyze_code", self.code_analysis_node)
        workflow.add_node("analyze_knowledge_graph", self.knowledge_graph_analysis_node)  # NEW
        workflow.add_node("detect_patterns", self.pattern_detection_node)
        workflow.add_node("generate_insights", self.generate_insights_node)
        workflow.add_node("compile_brief", self.compile_brief_node)
        
        # Add edges
        workflow.add_edge(START, "analyze_events")
        workflow.add_edge("analyze_events", "analyze_code")
        workflow.add_edge("analyze_code", "analyze_knowledge_graph")  # NEW: KG after code analysis
        workflow.add_edge("analyze_knowledge_graph", "detect_patterns")  # NEW: Pattern detection after KG
        workflow.add_edge("detect_patterns", "generate_insights")
        workflow.add_edge("generate_insights", "compile_brief")
        workflow.add_edge("compile_brief", END)
        
        return workflow.compile()
    
    async def analyze_events_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 1: Analyze and categorize events"""
        logger.info("🔍 Node 1: Analyzing events...")
        
        # Ensure we have a valid state
        if state is None:
            logger.error("❌ Node 1: Received None state!")
            state = {}
        
        logger.debug(f"📋 Node 1: Input state keys: {list(state.keys()) if state else 'None'}")
        
        events = state.get("events", [])
        
        # Categorize events
        event_categories = {
            "file_changes": [e for e in events if e.get("type") == "file_changed"],
            "git_commits": [e for e in events if e.get("type") == "git_commit"],
            "build_events": [e for e in events if e.get("type") == "build_event"],
            "error_events": [e for e in events if e.get("type") == "error_event"],
            "test_events": [e for e in events if e.get("type") == "test_event"]
        }
        
        # Basic statistics
        event_stats = {
            "total_events": len(events),
            "categories": {cat: len(evts) for cat, evts in event_categories.items()},
            "time_span": self._calculate_time_span(events),
            "activity_score": self._calculate_activity_score(event_categories)
        }
        
        # Add initial message
        initial_msg = HumanMessage(content=f"Analyzing {len(events)} development events for {state.get('developer_id', 'unknown')}")
        
        # Return new state
        new_state = dict(state)
        new_state.update({
            "event_categories": event_categories,
            "event_stats": event_stats,
            "messages": [initial_msg]
        })
        
        logger.debug(f"📋 Node 1: Output state keys: {list(new_state.keys())}")
        return new_state
    
    async def code_analysis_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 2: Deep code analysis using enhanced real-world tools"""
        logger.info("🧠 Node 2: Performing enhanced code analysis...")
        
        # Ensure we have a valid state
        if state is None:
            state = {}
        
        event_categories = state.get("event_categories", {})
        file_changes = event_categories.get("file_changes", [])
        
        # Run enhanced analysis with real security and quality tools
        try:
            enhanced_analysis = await run_enhanced_analysis(str(self.settings.project_root if hasattr(self.settings, 'project_root') else "."))
            
            # Format the analysis results to match expected structure
            code_analysis = {
                "total_files": enhanced_analysis.get("total_files_analyzed", 0),
                "languages_detected": enhanced_analysis.get("languages_detected", []),
                "security_issues": enhanced_analysis.get("security_issues", []),
                "quality_issues": enhanced_analysis.get("quality_issues", []),
                "analysis_tools_used": enhanced_analysis.get("analysis_tools_used", []),
                "security_concerns": enhanced_analysis.get("security_issues", []),  # For backward compatibility
                "suggestions": []  # Will be populated in insights node
            }
            
            logger.info(f"🔍 Enhanced analysis found {len(code_analysis['security_issues'])} security issues and {len(code_analysis['quality_issues'])} quality issues")
        
        except Exception as e:
            logger.error(f"Enhanced analysis failed, falling back to basic analysis: {e}")
            # Fallback to original analysis
            code_analysis = await self.code_analyzer.analyze_code_changes(file_changes)
        
        # Analyze build patterns (keep existing logic)
        build_events = event_categories.get("build_events", [])
        build_analysis = await self.code_analyzer.analyze_build_patterns(build_events)
        
        # Add analysis message
        total_issues = len(code_analysis.get('security_issues', [])) + len(code_analysis.get('quality_issues', []))
        analysis_msg = AIMessage(
            content=f"Enhanced code analysis complete: {code_analysis.get('total_files', 0)} files analyzed, "
                   f"{total_issues} total issues found using {len(code_analysis.get('analysis_tools_used', []))} tools"
        )
        
        # Return new state
        new_state = dict(state)
        new_state.update({
            "code_analysis": code_analysis,
            "build_analysis": build_analysis,
            "messages": state.get("messages", []) + [analysis_msg]
        })
        return new_state
    
    async def knowledge_graph_analysis_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 3: Get insights from Knowledge Graph based on recent changes"""
        logger.info("🧠 Node 3: Analyzing Knowledge Graph insights...")
        
        # Ensure we have a valid state
        if state is None:
            state = {}
        
        developer_id = state.get("developer_id", "unknown")
        event_categories = state.get("event_categories", {})
        file_changes = event_categories.get("file_changes", [])
        code_analysis = state.get("code_analysis", {})
        
        knowledge_graph_insights = {
            "contextual_knowledge": None,
            "code_evaluation": None,
            "pattern_matches": [],
            "relevant_documentation": [],
            "recommendations": [],
            "golden_source_alignment": 0.0,
            "coverage_gaps": [],
            "error": None
        }
        
        try:
            if self.knowledge_graph_service and self.knowledge_graph_service.is_initialized:
                logger.info(f"🔍 Getting Knowledge Graph insights for {developer_id}")
                
                # Extract context from recent changes
                current_files = []
                languages = set()
                recent_changes_data = []
                
                for change in file_changes[:5]:  # Analyze top 5 recent changes
                    file_path = change.get("file_path", "")
                    if file_path:
                        current_files.append(file_path)
                        # Extract language from file extension
                        if "." in file_path:
                            ext = file_path.split(".")[-1].lower()
                            lang_mapping = {
                                "py": "python", "js": "javascript", "ts": "typescript",
                                "java": "java", "kt": "kotlin", "go": "go", "rs": "rust"
                            }
                            if ext in lang_mapping:
                                languages.add(lang_mapping[ext])
                    
                    recent_changes_data.append({
                        "file_path": file_path,
                        "description": change.get("description", ""),
                        "type": change.get("type", ""),
                        "metadata": change.get("metadata", {})
                    })
                
                primary_language = list(languages)[0] if languages else None
                current_file = current_files[0] if current_files else None
                
                # 1. Get contextual knowledge
                try:
                    contextual_knowledge = await self.knowledge_graph_service.get_relevant_context(
                        developer_id=developer_id,
                        current_file=current_file,
                        language=primary_language,
                        recent_changes=recent_changes_data
                    )
                    knowledge_graph_insights["contextual_knowledge"] = {
                        "relevant_sources": contextual_knowledge.relevant_sources,
                        "similar_patterns": [
                            {
                                "pattern_name": p.pattern_name,
                                "source_id": p.source_id,
                                "confidence": p.confidence,
                                "description": p.description[:150] + "..." if len(p.description) > 150 else p.description
                            }
                            for p in contextual_knowledge.similar_patterns[:3]
                        ],
                        "related_documentation": [
                            {
                                "title": d.title,
                                "source_id": d.source_id,
                                "similarity_score": d.similarity_score,
                                "url": d.url
                            }
                            for d in contextual_knowledge.related_documentation[:3]
                        ],
                        "context_score": contextual_knowledge.context_score
                    }
                    
                    # Extract recommendations from contextual knowledge
                    knowledge_graph_insights["recommendations"].extend([
                        {
                            "type": "knowledge_graph",
                            "title": rec.title,
                            "description": rec.description,
                            "priority": rec.priority.value,
                            "source": "contextual_knowledge"
                        }
                        for rec in contextual_knowledge.recommendations[:3]
                    ])
                    
                except Exception as e:
                    logger.warning(f"Failed to get contextual knowledge: {e}")
                
                # 2. Evaluate recent changes against golden sources
                if recent_changes_data:
                    try:
                        # Combine recent changes for evaluation
                        combined_content = "\n".join([
                            f"# {change['file_path']}\n{change['description']}"
                            for change in recent_changes_data[:3]
                        ])
                        
                        if combined_content.strip():
                            code_evaluation = await self.knowledge_graph_service.evaluate_code_against_golden_sources(
                                developer_id=developer_id,
                                code_content=combined_content,
                                file_path="; ".join(current_files[:3]),
                                language=primary_language,
                                context={
                                    "recent_changes": len(recent_changes_data),
                                    "analysis_context": code_analysis
                                }
                            )
                            
                            knowledge_graph_insights["code_evaluation"] = {
                                "overall_alignment_score": code_evaluation.overall_alignment_score,
                                "quality_score": code_evaluation.quality_score,
                                "security_score": code_evaluation.security_score,
                                "maintainability_score": code_evaluation.maintainability_score,
                                "pattern_matches_count": len(code_evaluation.pattern_matches),
                                "recommendations_count": len(code_evaluation.recommendations),
                                "evaluation_id": code_evaluation.evaluation_id
                            }
                            
                            knowledge_graph_insights["golden_source_alignment"] = code_evaluation.overall_alignment_score
                            knowledge_graph_insights["coverage_gaps"] = code_evaluation.coverage_gaps
                            
                            # Add pattern matches
                            knowledge_graph_insights["pattern_matches"] = [
                                {
                                    "pattern_name": p.pattern_name,
                                    "source_id": p.source_id,
                                    "confidence": p.confidence,
                                    "similarity_score": p.similarity_score,
                                    "description": p.description[:100] + "..." if len(p.description) > 100 else p.description
                                }
                                for p in code_evaluation.pattern_matches[:5]
                            ]
                            
                            # Add evaluation recommendations
                            knowledge_graph_insights["recommendations"].extend([
                                {
                                    "type": "code_evaluation",
                                    "title": rec.title,
                                    "description": rec.description,
                                    "priority": rec.priority.value,
                                    "source": "code_evaluation",
                                    "source_reference": rec.source_reference
                                }
                                for rec in code_evaluation.recommendations[:3]
                            ])
                        
                    except Exception as e:
                        logger.warning(f"Failed to evaluate code against golden sources: {e}")
                
            else:
                logger.info("Knowledge Graph service not available, skipping KG analysis")
                knowledge_graph_insights["error"] = "Knowledge Graph service not available"
                
        except Exception as e:
            logger.error(f"Knowledge Graph analysis failed: {e}")
            knowledge_graph_insights["error"] = str(e)
        
        # Create analysis message
        insights_count = len(knowledge_graph_insights.get("pattern_matches", [])) + len(knowledge_graph_insights.get("recommendations", []))
        kg_msg = AIMessage(
            content=f"Knowledge Graph analysis complete: {insights_count} insights generated, "
                   f"alignment score: {knowledge_graph_insights.get('golden_source_alignment', 0.0):.2f}"
        )
        
        # Return new state
        new_state = dict(state)
        new_state.update({
            "knowledge_graph_insights": knowledge_graph_insights,
            "messages": state.get("messages", []) + [kg_msg]
        })
        return new_state
    
    async def pattern_detection_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 3: Advanced pattern detection using LLM"""
        logger.info("🔮 Node 3: Detecting patterns...")
        
        # Ensure we have a valid state
        if state is None:
            state = {}
        
        if not self.llm:
            logger.warning("No LLM available for pattern detection")
            pattern_analysis = {
                "patterns": [], 
                "insights": [],
                "patterns_identified": [],
                "risk_indicators": [],
                "recommendations": []
            }
            pattern_msg = AIMessage(content="Pattern detection failed")
        else:
            try:
                # Prepare data for LLM analysis
                code_analysis = state.get("code_analysis", {})
                build_analysis = state.get("build_analysis", {})
                event_stats = state.get("event_stats", {})
                
                # Create comprehensive prompt for pattern detection
                pattern_prompt = ChatPromptTemplate.from_template("""
                You are an expert software engineering AI analyzing a developer's recent activity.
                
                Event Summary:
                - Total events: {total_events}
                - File changes: {file_changes}
                - Commits: {commits}
                - Builds: {builds}
                - Activity score: {activity_score}/10
                
                Code Analysis:
                - Languages detected: {languages}
                - Quality issues: {quality_issues}
                - Security concerns: {security_concerns}
                - Complexity analysis: {complexity}
                
                Build Analysis:
                - Success rate: {build_success_rate}
                - Failure patterns: {build_failures}
                
                Please identify:
                1. **Productivity Patterns**: What patterns indicate high/low productivity?
                2. **Quality Trends**: Are there recurring quality issues?
                3. **Risk Indicators**: What suggests potential problems?
                4. **Positive Behaviors**: What's working well?
                5. **Improvement Opportunities**: Specific, actionable recommendations
                
                Respond in JSON format with structured insights.
                """)
                
                pattern_input = {
                    "total_events": event_stats.get("total_events", 0),
                    "file_changes": event_stats.get("categories", {}).get("file_changes", 0),
                    "commits": event_stats.get("categories", {}).get("git_commits", 0),
                    "builds": event_stats.get("categories", {}).get("build_events", 0),
                    "activity_score": event_stats.get("activity_score", 0),
                    "languages": code_analysis.get("languages_detected", []),
                    "quality_issues": len(code_analysis.get("quality_issues", [])),
                    "security_concerns": len(code_analysis.get("security_concerns", [])),
                    "complexity": code_analysis.get("complexity_analysis", {}),
                    "build_success_rate": build_analysis.get("success_rate", 1.0),
                    "build_failures": build_analysis.get("failure_patterns", {})
                }
                
                messages = pattern_prompt.format_messages(**pattern_input)
                response = await self.llm.ainvoke(messages)
                
                # Parse LLM response (simplified - would use structured output in production)
                pattern_analysis = {
                    "raw_llm_response": response.content,
                    "patterns_identified": self._extract_patterns_from_llm_response(response.content),
                    "risk_indicators": self._extract_risks_from_llm_response(response.content),
                    "recommendations": self._extract_recommendations_from_llm_response(response.content)
                }
                
                pattern_msg = AIMessage(content=f"Pattern analysis complete: {len(pattern_analysis['patterns_identified'])} patterns identified")
                
            except Exception as e:
                logger.error(f"Pattern detection failed: {e}")
                pattern_analysis = {"patterns": [], "insights": [], "error": str(e)}
                pattern_msg = AIMessage(content="Pattern detection failed")
        
        # Return new state
        new_state = dict(state)
        new_state.update({
            "pattern_analysis": pattern_analysis,
            "messages": state.get("messages", []) + [pattern_msg]
        })
        return new_state
    
    async def generate_insights_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 5: Generate critical insights and suggestions (Enhanced with Knowledge Graph)"""
        logger.info("💡 Node 5: Generating insights with Knowledge Graph integration...")
        
        # Ensure we have a valid state
        if state is None:
            state = {}
        
        code_analysis = state.get("code_analysis", {})
        pattern_analysis = state.get("pattern_analysis", {})
        knowledge_graph_insights = state.get("knowledge_graph_insights", {})  # NEW: KG insights
        event_stats = state.get("event_stats", {})
        
        # Generate critical insights with detailed file information
        critical_insights = []
        
        # Knowledge Graph alignment issues (NEW)
        kg_alignment = knowledge_graph_insights.get("golden_source_alignment", 0.0)
        if kg_alignment < 0.5 and kg_alignment > 0:  # Only show if we have data and it's concerning
            critical_insights.append({
                "type": "golden_source_alignment",
                "priority": "high" if kg_alignment < 0.3 else "medium",
                "title": f"Low alignment with golden sources ({kg_alignment:.1%})",
                "description": f"Recent changes don't align well with established patterns from golden sources",
                "action_required": True,
                "count": len(knowledge_graph_insights.get("pattern_matches", [])),
                "files": [],
                "source": "knowledge_graph"
            })
        
        # Knowledge Graph coverage gaps (NEW)
        coverage_gaps = knowledge_graph_insights.get("coverage_gaps", [])
        if coverage_gaps:
            critical_insights.append({
                "type": "knowledge_coverage",
                "priority": "medium",
                "title": f"Knowledge coverage gaps identified",
                "description": f"Found {len(coverage_gaps)} areas lacking golden source guidance",
                "action_required": False,
                "count": len(coverage_gaps),
                "files": [],
                "details": coverage_gaps[:3],  # Include first 3 gaps
                "source": "knowledge_graph"
            })
        
        # Security issues with file details
        security_issues = code_analysis.get("security_issues", [])
        if security_issues:
            # Group by severity to determine priority
            critical_security = [i for i in security_issues if i.get("severity") in ["critical", "high"]]
            
            if critical_security:
                critical_insights.append({
                    "type": "security",
                    "priority": "critical",
                    "title": "Security concerns detected",
                    "description": f"Found {len(security_issues)} potential security issues",
                    "action_required": True,
                    "count": len(security_issues),
                    "files": security_issues,  # Include all file details
                    "source": "code_analysis"
                })
        
        # Build failures
        build_analysis = state.get("build_analysis", {})
        if build_analysis.get("failed_builds", 0) > 0:
            critical_insights.append({
                "type": "build_failure",
                "priority": "high",
                "title": f"{build_analysis['failed_builds']} build failures",
                "description": "Recent builds have failed and may block progress",
                "action_required": True,
                "count": build_analysis.get("failed_builds", 0),
                "files": [],  # Could add build log file paths if available
                "source": "code_analysis"
            })
        
        # Quality issues with file details
        quality_issues = code_analysis.get("quality_issues", [])
        if quality_issues:
            # Group by severity
            high_quality_issues = [i for i in quality_issues if i.get("severity") in ["high", "medium"]]
            
            if high_quality_issues:
                critical_insights.append({
                    "type": "code_quality",
                    "priority": "medium",
                    "title": "Code quality attention needed",
                    "description": f"Identified {len(quality_issues)} quality concerns",
                    "action_required": False,
                    "count": len(quality_issues),
                    "files": quality_issues,  # Include all file details
                    "source": "code_analysis"
                })
        
        # Generate suggestions with enhanced file details and Knowledge Graph recommendations
        suggestions = []
        
        # Knowledge Graph recommendations (NEW - highest priority)
        kg_recommendations = knowledge_graph_insights.get("recommendations", [])
        for rec in kg_recommendations[:3]:  # Top 3 KG recommendations
            suggestions.append({
                "type": rec.get("type", "knowledge_graph"),
                "title": rec["title"],
                "description": rec["description"],
                "priority": rec.get("priority", "medium"),
                "action": "review_golden_sources",
                "source": rec.get("source", "knowledge_graph"),
                "source_reference": rec.get("source_reference"),
                "files": []
            })
        
        # Pattern matches from Knowledge Graph (NEW)
        pattern_matches = knowledge_graph_insights.get("pattern_matches", [])
        if pattern_matches:
            suggestions.append({
                "type": "pattern_alignment",
                "title": f"Review {len(pattern_matches)} similar patterns from golden sources",
                "description": f"Found patterns in golden sources that could guide current development",
                "priority": "medium",
                "action": "review_patterns",
                "source": "knowledge_graph",
                "pattern_details": [
                    {
                        "name": p["pattern_name"],
                        "source": p["source_id"],
                        "confidence": p["confidence"]
                    }
                    for p in pattern_matches[:3]
                ],
                "files": []
            })
        
        # Documentation recommendations from Knowledge Graph (NEW)
        kg_contextual = knowledge_graph_insights.get("contextual_knowledge", {})
        if kg_contextual:
            related_docs = kg_contextual.get("related_documentation", [])
            if related_docs:
                suggestions.append({
                    "type": "documentation",
                    "title": f"Review {len(related_docs)} relevant documentation sources",
                    "description": "Found documentation that may help with current development context",
                    "priority": "low",
                    "action": "review_documentation",
                    "source": "knowledge_graph",
                    "documentation": [
                        {
                            "title": doc["title"],
                            "source": doc["source_id"],
                            "url": doc["url"]
                        }
                        for doc in related_docs
                    ],
                    "files": []
                })
        
        # From security analysis
        if security_issues:
            security_files = [i for i in security_issues if i.get("severity") in ["medium", "low"]]
            if security_files:
                suggestions.append({
                    "type": "security",
                    "title": "Review security implications",
                    "description": f"Identified {len(security_issues)} security considerations",
                    "priority": "high",
                    "action": "security_review",
                    "source": "code_analysis",
                    "files": security_files
                })
        
        # From quality analysis  
        if quality_issues:
            quality_files = [i for i in quality_issues if i.get("severity") in ["low", "medium"]]
            if quality_files:
                suggestions.append({
                    "type": "quality",
                    "title": "Address code quality issues",
                    "description": f"Found {len(quality_issues)} potential quality concerns",
                    "priority": "medium",
                    "action": "quality_review",
                    "source": "code_analysis",
                    "files": quality_files
                })
        
        # From pattern analysis
        pattern_recommendations = pattern_analysis.get("recommendations", [])
        for rec in pattern_recommendations:
            suggestions.append({
                "type": "pattern_based",
                "title": rec.get("title", "LLM Recommendation"),
                "description": rec.get("description", "Based on pattern analysis"),
                "priority": rec.get("priority", "medium"),
                "action": None,
                "source": "llm_analysis",
                "files": []
            })
        
        # Activity-based suggestions
        activity_score = event_stats.get("activity_score", 0)
        if activity_score < 3:
            suggestions.append({
                "type": "productivity",
                "title": "Low activity detected",
                "description": "Consider setting small, achievable development goals",
                "priority": "low",
                "action": None,
                "source": "activity_analysis",
                "files": []
            })
        elif activity_score > 8:
            suggestions.append({
                "type": "wellness",
                "title": "High activity - remember work-life balance",
                "description": "Great productivity! Don't forget to take breaks",
                "priority": "low",
                "action": None,
                "source": "activity_analysis",
                "files": []
            })
        
        # Sort suggestions by priority (Knowledge Graph first, then by priority level)
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        suggestions.sort(key=lambda s: (
            1 if s.get("source") == "knowledge_graph" else 0,  # KG suggestions first
            priority_order.get(s.get("priority", "low"), 1)
        ), reverse=True)
        
        insights_msg = AIMessage(
            content=f"Generated {len(critical_insights)} critical insights and {len(suggestions)} suggestions "
                   f"(including {len(kg_recommendations)} from Knowledge Graph)"
        )
        
        # Return new state
        new_state = dict(state)
        new_state.update({
            "critical_insights": critical_insights,
            "suggestions": suggestions,
            "messages": state.get("messages", []) + [insights_msg]
        })
        return new_state
    
    async def compile_brief_node(self, state: MorningBriefState) -> MorningBriefState:
        """Node 6: Compile final morning brief (Enhanced with Knowledge Graph)"""
        logger.info("📋 Node 6: Compiling morning brief with Knowledge Graph insights...")
        
        # Ensure we have a valid state
        if state is None:
            logger.error("❌ Node 6: Received None state!")
            state = {}
        
        logger.debug(f"📋 Node 6: State keys: {list(state.keys()) if state else 'None'}")
        
        if not self.llm:
            return self._compile_basic_brief(state)
        
        # Create sophisticated brief using LLM
        return await self._compile_llm_brief(state)
    
    async def _compile_llm_brief(self, state: MorningBriefState) -> MorningBriefState:
        """Compile brief using LLM for natural language generation (Enhanced with KG)"""
        
        # Prepare comprehensive context
        event_stats = state.get("event_stats", {})
        code_analysis = state.get("code_analysis", {})
        knowledge_graph_insights = state.get("knowledge_graph_insights", {})  # NEW: KG insights
        critical_insights = state.get("critical_insights", [])
        suggestions = state.get("suggestions", [])
        
        # Enhanced prompt with Knowledge Graph context
        brief_prompt = ChatPromptTemplate.from_template("""
        You are an AI assistant creating a morning brief for a software developer.
        Be concise, actionable, and encouraging. Focus on what matters most.
        
        Developer: {developer_id}
        
        Recent Activity (last 24h):
        - {total_events} total events
        - {files_changed} files modified
        - {commits} commits made
        - {builds} builds triggered
        - Activity level: {activity_score}/10
        
        Code Analysis:
        - Languages worked on: {languages}
        - Security issues: {security_count}
        - Quality concerns: {quality_count}
        - Build success rate: {build_success_rate}%
        
        Knowledge Graph Insights:
        - Golden source alignment: {golden_source_alignment:.1%}
        - Pattern matches found: {pattern_matches_count}
        - Relevant documentation: {documentation_count}
        - Knowledge recommendations: {kg_recommendations_count}
        
        Critical Items Needing Attention:
        {critical_items}
        
        Top Recommendations:
        {suggestions_text}
        
        Create a concise, friendly morning brief (2-3 paragraphs) that:
        1. Acknowledges their recent work and golden source alignment
        2. Highlights the most important items needing attention
        3. Provides 2-3 specific, actionable recommendations (prioritizing Knowledge Graph insights)
        4. Mentions relevant patterns or documentation from golden sources
        5. Ends on an encouraging note
        
        Keep it conversational and supportive, emphasizing how golden sources can guide their work.
        """)
        
        try:
            # Format critical items
            critical_items_text = "\n".join([
                f"• {item['title']}: {item['description']}" 
                for item in critical_insights[:3]
            ]) if critical_insights else "• No critical issues detected"
            
            # Format suggestions (prioritize KG suggestions)
            suggestions_text = "\n".join([
                f"• {sug['title']}: {sug['description']}" 
                for sug in suggestions[:4]  # Show top 4 suggestions
            ]) if suggestions else "• Keep up the great work!"
            
            # Prepare Knowledge Graph metrics
            kg_alignment = knowledge_graph_insights.get("golden_source_alignment", 0.0)
            pattern_matches = knowledge_graph_insights.get("pattern_matches", [])
            kg_contextual = knowledge_graph_insights.get("contextual_knowledge", {})
            related_docs = kg_contextual.get("related_documentation", []) if kg_contextual else []
            kg_recommendations = knowledge_graph_insights.get("recommendations", [])
            
            brief_input = {
                "developer_id": state.get("developer_id", "unknown"),
                "total_events": event_stats.get("total_events", 0),
                "files_changed": event_stats.get("categories", {}).get("file_changes", 0),
                "commits": event_stats.get("categories", {}).get("git_commits", 0),
                "builds": event_stats.get("categories", {}).get("build_events", 0),
                "activity_score": event_stats.get("activity_score", 0),
                "languages": ", ".join(code_analysis.get("languages_detected", [])) or "None detected",
                "security_count": len(code_analysis.get("security_issues", [])),
                "quality_count": len(code_analysis.get("quality_issues", [])),
                "build_success_rate": int(state.get("build_analysis", {}).get("success_rate", 1.0) * 100),
                "golden_source_alignment": kg_alignment,
                "pattern_matches_count": len(pattern_matches),
                "documentation_count": len(related_docs),
                "kg_recommendations_count": len(kg_recommendations),
                "critical_items": critical_items_text,
                "suggestions_text": suggestions_text
            }
            
            messages = brief_prompt.format_messages(**brief_input)
            response = await self.llm.ainvoke(messages)
            
            # Create final brief with enhanced Knowledge Graph insights
            morning_brief = {
                "developer_id": state.get("developer_id", "unknown"),
                "generated_at": datetime.now().isoformat(),
                "status": "success",
                "greeting": "Good morning! Here's your intelligent development summary with insights from your golden sources.",
                "summary": response.content,
                "activity_overview": {
                    **event_stats.get("categories", {}),
                    "activity_score": event_stats.get("activity_score", 0),
                    "time_span": event_stats.get("time_span", "24 hours"),
                    "languages_used": code_analysis.get("languages_detected", [])
                },
                "critical_items": critical_insights,
                "suggestions": suggestions,
                "knowledge_graph_insights": {  # NEW: Include KG insights in the response
                    "golden_source_alignment": kg_alignment,
                    "pattern_matches_count": len(pattern_matches),
                    "top_pattern_matches": pattern_matches[:3],
                    "relevant_documentation_count": len(related_docs),
                    "top_documentation": related_docs[:3],
                    "recommendations_count": len(kg_recommendations),
                    "coverage_gaps_count": len(knowledge_graph_insights.get("coverage_gaps", [])),
                    "contextual_sources": kg_contextual.get("relevant_sources", []) if kg_contextual else [],
                    "context_score": kg_contextual.get("context_score", 0.0) if kg_contextual else 0.0
                },
                "insights": {
                    "code_quality_score": 10 - len(code_analysis.get("quality_issues", [])),
                    "build_health": state.get("build_analysis", {}).get("success_rate", 1.0),
                    "patterns_detected": len(state.get("pattern_analysis", {}).get("patterns_identified", [])),
                    "golden_source_alignment": kg_alignment,  # NEW: Include in insights
                    "knowledge_graph_available": knowledge_graph_insights.get("error") is None,  # NEW
                    "generated_by": "LangGraph Workflow with Knowledge Graph",
                    "workflow_version": "2.0"
                }
            }
            
            final_msg = AIMessage(content="Morning brief compilation complete with Knowledge Graph insights!")
            
            # Fix the return statement syntax
            result_state = dict(state) if state else {}
            result_state["morning_brief"] = morning_brief
            result_state["messages"] = state.get("messages", []) + [final_msg] if state else [final_msg]
            return result_state
        
        except Exception as e:
            logger.error(f"LLM brief compilation failed: {e}")
            return self._compile_basic_brief(state)
    
    def _compile_basic_brief(self, state: MorningBriefState) -> MorningBriefState:
        """Fallback: compile basic brief without LLM (Enhanced with KG)"""
        # Safely get state values with proper None checking
        event_stats = state.get("event_stats") if state else None
        critical_insights = state.get("critical_insights") if state else None
        suggestions = state.get("suggestions") if state else None
        knowledge_graph_insights = state.get("knowledge_graph_insights", {}) if state else {}  # NEW
        
        # Ensure we have proper defaults if values are None
        if event_stats is None:
            event_stats = {"total_events": 0, "categories": {}}
        if critical_insights is None:
            critical_insights = []
        if suggestions is None:
            suggestions = []
        
        # Generate basic summary with Knowledge Graph context
        total_events = event_stats.get("total_events", 0) if event_stats else 0
        kg_alignment = knowledge_graph_insights.get("golden_source_alignment", 0.0)
        pattern_matches = len(knowledge_graph_insights.get("pattern_matches", []))
        
        if total_events == 0:
            summary = "Good morning! No recent development activity detected. Ready to start fresh!"
        else:
            summary = f"Good morning! You had {total_events} development events recently. "
            if kg_alignment > 0:
                summary += f"Your changes align {kg_alignment:.0%} with golden source patterns. "
            if pattern_matches > 0:
                summary += f"Found {pattern_matches} relevant patterns from your golden sources. "
            if critical_insights:
                summary += f"There are {len(critical_insights)} items needing your attention. "
            summary += "Have a productive day!"
        
        morning_brief = {
            "developer_id": state.get("developer_id", "unknown") if state else "unknown",
            "generated_at": datetime.now().isoformat(),
            "status": "success",
            "greeting": "Good morning! Here's your development summary with basic Knowledge Graph insights.",
            "summary": summary,
            "activity_overview": event_stats.get("categories", {}) if event_stats else {},
            "critical_items": critical_insights,
            "suggestions": suggestions,
            "knowledge_graph_insights": {  # NEW: Include KG insights even in basic mode
                "golden_source_alignment": kg_alignment,
                "pattern_matches_count": pattern_matches,
                "available": knowledge_graph_insights.get("error") is None
            },
            "insights": {
                "generated_by": "Basic Workflow with Knowledge Graph",
                "workflow_version": "2.0"
            }
        }
        
        # Fix the return statement syntax
        result_state = dict(state) if state else {}
        result_state["morning_brief"] = morning_brief
        return result_state
    
    # Helper methods
    def _calculate_time_span(self, events: List[Dict[str, Any]]) -> str:
        """Calculate time span of events"""
        if not events:
            return "0 hours"
        
        timestamps = []
        for event in events:
            try:
                timestamp = datetime.fromisoformat(event.get("timestamp", ""))
                timestamps.append(timestamp)
            except (ValueError, TypeError):
                continue
        
        if not timestamps:
            return "24 hours"
        
        timestamps.sort()
        time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
        return f"{time_span:.1f} hours"
    
    def _calculate_activity_score(self, event_categories: Dict[str, List]) -> int:
        """Calculate activity score (0-10)"""
        score = 0
        
        # File changes (up to 3 points)
        file_changes = len(event_categories.get("file_changes", []))
        score += min(3, file_changes * 0.3)
        
        # Commits (up to 4 points)
        commits = len(event_categories.get("git_commits", []))
        score += min(4, commits * 1.0)
        
        # Builds (up to 2 points)
        builds = len(event_categories.get("build_events", []))
        score += min(2, builds * 0.5)
        
        # Tests (up to 1 point)
        tests = len(event_categories.get("test_events", []))
        score += min(1, tests * 0.2)
        
        return min(10, int(score))
    
    def _extract_patterns_from_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract patterns from LLM response (simplified)"""
        patterns = []
        if "pattern" in response.lower():
            patterns.append({"type": "productivity", "description": "Productivity pattern detected"})
        if "quality" in response.lower():
            patterns.append({"type": "quality", "description": "Quality pattern detected"})
        return patterns
    
    def _extract_risks_from_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract risk indicators from LLM response"""
        risks = []
        if "risk" in response.lower() or "warning" in response.lower():
            risks.append({"type": "general", "description": "Risk indicator detected"})
        return risks
    
    def _extract_recommendations_from_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract recommendations from LLM response"""
        recommendations = []
        if "recommend" in response.lower() or "suggest" in response.lower():
            recommendations.append({
                "title": "LLM Recommendation",
                "description": "Based on pattern analysis",
                "priority": "medium"
            })
        return recommendations
    
    async def run(self, initial_state: MorningBriefState) -> Dict[str, Any]:
        """Run the complete workflow"""
        developer_id = initial_state.get("developer_id", "unknown") if initial_state else "unknown"
        logger.info(f"🚀 Starting Morning Brief Workflow for {developer_id}")
        
        try:
            # Execute the workflow
            logger.debug(f"📋 Running workflow with initial state keys: {list(initial_state.keys()) if initial_state else 'None'}")
            final_state = await self.workflow.ainvoke(initial_state)
            
            # Debug final state
            logger.debug(f"📋 Final state keys: {list(final_state.keys()) if final_state else 'None'}")
            
            # Extract the morning brief
            morning_brief = final_state.get("morning_brief") if final_state else None
            logger.debug(f"📋 Morning brief found: {morning_brief is not None}")
            
            if not morning_brief:
                # Let's check what we actually got
                logger.error(f"❌ No morning brief in final state. Available keys: {list(final_state.keys()) if final_state else 'None'}")
                raise ValueError("Workflow failed to generate morning brief")
            
            logger.info("✅ Morning Brief Workflow completed successfully")
            return morning_brief
            
        except Exception as e:
            logger.error(f"❌ Morning Brief Workflow failed: {e}")
            
            # Return error brief
            return {
                "developer_id": developer_id,
                "generated_at": datetime.now().isoformat(),
                "status": "error",
                "summary": f"Failed to generate morning brief: {str(e)}",
                "activity_overview": {},
                "critical_items": [],
                "suggestions": [],
                "insights": {"error": str(e)}
            }

async def create_morning_brief_workflow(knowledge_graph_service=None) -> MorningBriefWorkflow:
    """Create and return the morning brief workflow with Knowledge Graph integration"""
    logger.info("🔄 Creating LangGraph Morning Brief Workflow with Knowledge Graph integration...")
    
    settings = get_settings()
    workflow = MorningBriefWorkflow(
        openai_api_key=settings.openai_api_key,
        knowledge_graph_service=knowledge_graph_service  # NEW: Pass KG service
    )
    
    if knowledge_graph_service and knowledge_graph_service.is_initialized:
        logger.info("✅ LangGraph Morning Brief Workflow ready with Knowledge Graph service")
    else:
        logger.info("✅ LangGraph Morning Brief Workflow ready (without Knowledge Graph service)")
    
    return workflow 