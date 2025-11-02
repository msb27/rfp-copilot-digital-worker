# test_agent.py
from agent import run_with_audit

sample_rfp = """
RFP Title: Phase III Oncology Trial Support
Client: AstraZeneca
Submission Deadline: December 15, 2025
Budget Range: $3.2M – $4.1M
Project Duration: 24 months
Scope: 
- Global site selection across 40+ countries
- Patient recruitment with adaptive design
- Central imaging review
- Real-world evidence integration
Key Requirements:
1. Proven adaptive trial experience
2. RWE platform integration
3. Veeva Vault compliance
"""

if __name__ == "__main__":
    output, audit = run_with_audit(sample_rfp)
    print("\nFINAL RESPONSE:\n")
    print(output)