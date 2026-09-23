target_product: Riskfolio-Lib
expected_version: "7.3.0"
official_interface_to_use: "Python package API: riskfolio.Portfolio.optimization and riskfolio.Portfolio.rp_optimization"
proof_action: "Solve a constrained minimum-variance portfolio through the installed Riskfolio-Lib optimizer"
independent_oracle: "Independently calculate weight sum, per-asset bounds, and sample-covariance portfolio variance"
facade_failure_example: "A local optimizer or fabricated weights could pass wrapper-only assertions without Riskfolio-Lib executing"
