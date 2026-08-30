# Evaluation suite unit tests
from eval.eval_runner import run_evaluation


class TestEvaluationSuite:
    # Test evaluation suite execution

    def test_run_evaluation_passes(self):
        # Verify evaluation runner passes across golden dataset
        results = run_evaluation("eval/dataset.jsonl")
        assert results["total_samples"] >= 10
        assert results["route_accuracy"] >= 90.0
        assert results["status"] == "PASSED"
