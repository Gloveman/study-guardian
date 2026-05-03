# test_run.py
import os
from dotenv import load_dotenv

from src.parser import parse_multiple_notebooks
from src.architect import StudyArchitect

# 1. 테스트할 실제 파일 경로 (현재 폴더에 있는 모든 .ipynb 파일)
notebook_paths = [f for f in os.listdir(".") if f.endswith(".ipynb")]

if not notebook_paths:
    print("❌ 테스트할 .ipynb 파일이 현재 폴더에 없습니다. 파일을 하나 준비해 주세요!")
    exit()

# Chainlit 파일 객체를 흉내내는 가짜 클래스
class MockFile:
    def __init__(self, path):
        self.name = os.path.basename(path)
        with open(path, "rb") as f:
            self.content = f.read()

def run_test():
    print(f"🔎 {len(notebook_paths)}개의 파일을 찾았습니다: {notebook_paths}")
    
    # 2. 파서 가동
    mock_files = [MockFile(p) for p in notebook_paths]
    print("⚙️ 파싱 시작...")
    structured_data = parse_multiple_notebooks(mock_files)
    
    # 3. 아키텍트 가동
    print("🧠 아키텍트 지식 설계 중 (LLM 호출)...")
    architect = StudyArchitect('openai/gpt-oss-120b')
    final_note = architect.generate_notion_note(structured_data)
    
    # 4. 결과 저장
    output_filename = "Final_Study_Note.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_note)
    
    print("-" * 40)
    print(f"✅ 테스트 완료! '{output_filename}' 파일을 확인해 보세요.")
    print("-" * 40)

if __name__ == "__main__":
    load_dotenv()

    run_test()