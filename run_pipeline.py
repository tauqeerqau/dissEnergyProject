# ==========================================
# RUN PIPELINE (FINAL AUTOMATION SCRIPT)
# ==========================================

import subprocess
import sys
import os

# ==========================================
# HELPER FUNCTION
# ==========================================
def run_script(script_name):
    print(f"\n🚀 Running: {script_name}")

    result = subprocess.run(
        [sys.executable, script_name],
        capture_output=True,
        text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"❌ Error in {script_name}")
        print(result.stderr)
        sys.exit(1)
    else:
        print(f"✅ {script_name} completed successfully")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":

    print("===================================")
    print("⚡ ENERGY DATA PIPELINE STARTED")
    print("===================================")

    # ------------------------------------------
    # STEP 1: RUN DATA PIPELINE
    # ------------------------------------------
    run_script("data_pipeline.py")

    # ------------------------------------------
    # STEP 2: VALIDATE OUTPUT
    # ------------------------------------------
    print("\n🔍 Validating output...")

    if not os.path.exists("final_dataset.csv"):
        print("❌ final_dataset.csv not found!")
        sys.exit(1)

    if os.path.getsize("final_dataset.csv") == 0:
        print("❌ final_dataset.csv is empty!")
        sys.exit(1)

    print("✅ Output dataset validated successfully")

    # ------------------------------------------
    # STEP 3: OPTIONAL CHECK (analysis import)
    # ------------------------------------------
    try:
        import analysis
        print("✅ analysis.py loaded successfully")
    except Exception as e:
        print("⚠️ analysis.py not loaded (this is fine if using Streamlit)")
        print(e)

    # ------------------------------------------
    # FINAL MESSAGE
    # ------------------------------------------
    print("\n===================================")
    print("🎯 PIPELINE COMPLETED SUCCESSFULLY")
    print("===================================")

    print("\n👉 NEXT STEP:")
    print("Run the dashboard using:")
    print("\n    streamlit run app.py\n")