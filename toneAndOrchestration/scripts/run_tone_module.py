# scripts/run_tone_module.py
import sys
from tone_module.transformer import ToneTransformer

def main():
    print("=== Tone Module CLI ===")
    text = input("Enter text: ").strip()
    mode = input("Enter tone mode (formal/casual/concise/neutral): ").strip().lower()
    if mode not in {"formal", "casual", "concise", "neutral"}:
        print("Invalid mode, defaulting to neutral.")
        mode = "neutral"

    tt = ToneTransformer(mode=mode)
    out = tt.tone_transform(text, mode=mode)
    print("\n--- Transformed Output ---")
    print(out)
    print("--------------------------")

if __name__ == "__main__":
    sys.exit(main())
