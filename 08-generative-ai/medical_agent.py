"""
Module: summary_generator.py
Description: Synthesizes system risk reports into natural language executive updates.
"""
def generate_ai_report(device_id, anomaly_minutes):
    return (
        f"🤖 [GEN-AI EXECUTIVE SUMMARY]\n"
        f"Device '{device_id}' accumulated {anomaly_minutes:.2f} minutes of critical anomalies.\n"
        f"Recommended Action: Immediate hardware calibration and sensor inspection required."
    )

if __name__ == "__main__":
    print(generate_ai_report("DEV-CHARLIE", 57.5))