import argparse
from graph.workflow import run_pipeline
from config import SCORE_THRESHOLD


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resume and job description matching tool"
    )
    parser.add_argument(
        "--resume",
        required=True,
        help="Path to the resume file (PDF or DOCX)",
    )
    job_group = parser.add_mutually_exclusive_group(required=True)
    job_group.add_argument(
        "--job",
        help="Job description text",
    )
    job_group.add_argument(
        "--job-url",
        help="URL to the job description",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    job_source = args.job if args.job else args.job_url

    state = run_pipeline(resume_path=args.resume, job_source=job_source)

    print("\n" + "=" * 60)
    print("MATCH RESULTS")
    print("=" * 60)

    scores = state.get("scores", {})
    overall = scores.get("overall", 0.0)
    print(f"Overall Match Score: {overall:.2f}")

    print("\nCategory Breakdown:")
    print(f"  Skills:     {scores.get('skills', 0.0):.2f}")
    print(f"  Experience: {scores.get('experience', 0.0):.2f}")
    print(f"  Education:  {scores.get('education', 0.0):.2f}")
    print(f"  Keywords:   {scores.get('keywords', 0.0):.2f}")

    if overall >= SCORE_THRESHOLD:
        print("\n" + "=" * 60)
        print("INTERVIEW PREP PLAN")
        print("=" * 60)
        prep_plan = state.get("prep_plan", {})
        questions = prep_plan.get("questions", [])
        talking_points = prep_plan.get("talking_points", [])

        if questions:
            print("\nBehavioral Questions:")
            for i, question in enumerate(questions, 1):
                print(f"  {i}. {question}")

        if talking_points:
            print("\nTalking Points:")
            for i, point in enumerate(talking_points, 1):
                print(f"  {i}. {point}")
    else:
        print("\n" + "=" * 60)
        print("IMPROVEMENT SUGGESTIONS")
        print("=" * 60)
        improvements = state.get("improvements", [])
        if improvements:
            for i, suggestion in enumerate(improvements, 1):
                print(f"  {i}. {suggestion}")
        else:
            print("  No improvement suggestions available.")

        print("\n" + "=" * 60)
        print("GAP ANALYSIS")
        print("=" * 60)
        gaps = state.get("gaps", [])
        if gaps:
            for i, gap in enumerate(gaps, 1):
                print(f"  {i}. {gap}")
        else:
            print("  No gaps identified.")


if __name__ == "__main__":
    main()
