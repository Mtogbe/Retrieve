import glob
from ai import extract_resume_text

# run every pdf in test_resumes
for path in glob.glob("test_resumes/*.pdf"):
    with open(path, "rb") as f:
        text = extract_resume_text(f.read())
    print("=====", path, "=====")
    print("chars:", len(text))
    print(text[:500])
    print()

# edge cases should return ""
print("empty bytes:", repr(extract_resume_text(b"")))
print("not a pdf:", repr(extract_resume_text(b"hello world")))