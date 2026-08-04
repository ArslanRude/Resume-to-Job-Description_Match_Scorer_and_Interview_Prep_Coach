from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from graph.nodes import (
    ingest_resume,
    ingest_job,
    extract_resume,
    extract_job,
    review_resume,
    score_match,
    gap_analysis,
    interview_prep,
    resume_improvement,
    should_route,
)


class PipelineState(TypedDict, total=False):
    resume_path: str
    job_source: str
    resume_text: str
    job_text: str
    resume_schema: Any
    job_schema: Any
    scores: Dict[str, float]
    gaps: List[str]
    prep_plan: Dict[str, Any]
    improvements: List[str]


def build_graph() -> StateGraph:
    graph = StateGraph(PipelineState)

    graph.add_node('ingest_resume', ingest_resume)
    graph.add_node('ingest_job', ingest_job)
    graph.add_node('extract_resume', extract_resume)
    graph.add_node('extract_job', extract_job)
    graph.add_node('review_resume', review_resume)
    graph.add_node('score_match', score_match)
    graph.add_node('gap_analysis', gap_analysis)
    graph.add_node('interview_prep', interview_prep)
    graph.add_node('resume_improvement', resume_improvement)

    graph.set_entry_point('ingest_resume')
    graph.set_entry_point('ingest_job')

    graph.add_edge('ingest_resume', 'extract_resume')
    graph.add_edge('extract_resume', 'review_resume')
    graph.add_edge('ingest_job', 'extract_job')

    graph.add_edge('review_resume', 'score_match')
    graph.add_edge('extract_job', 'score_match')

    graph.add_edge('score_match', 'gap_analysis')

    graph.add_conditional_edges(
        'gap_analysis',
        should_route,
        {
            'interview_prep': 'interview_prep',
            'resume_improvement': 'resume_improvement',
        },
    )

    graph.add_edge('interview_prep', END)
    graph.add_edge('resume_improvement', END)

    return graph


def run_pipeline(resume_path: str, job_source: str) -> dict:
    graph = build_graph()
    compiled = graph.compile()
    initial_state: dict = {
        'resume_path': resume_path,
        'job_source': job_source,
    }
    result = compiled.invoke(initial_state)
    return result
