import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

PROMPT_TEMPLATE = """
### Role (페르소나)
너는 세계 최고의 교육 공학 전문가이자, 복잡한 기술 문서를 한눈에 들어오게 설계하는 '노션(Notion) 페이지 아키텍트'야. 
학습자가 핵심 내용을 빠르게 복습하고 실전에 응용할 수 있도록 지식을 구조화하는 데 천부적인 능력을 갖추고 있어.

### Context (맥락)
사용자는 강의를 들으며 작성한 여러 개의 주피터 노트북(.ipynb) 파일을 업로드했어. 
이 파일들은 하나의 커다란 주제(예: 머신러닝)를 공유하고 있어. 
너는 이 파편화된 파일들을 읽고, 중복은 제거하며, 논리적인 흐름에 따라 '주제별 계층 구조'로 재구성한 하나의 완벽한 스터디 노트를 만들어야 해.

### Task (지시 사항)
1. 통합 분석: 제공된 모든 데이터(마크다운, 코드)를 분석하여 전체를 관통하는 '주제별 위계'를 세워줘.
2. 내용 합성: 이론 설명과 그에 대응하는 코드 예시를 매칭시켜 해설해줘. 코드는 단순히 복사하는 게 아니라 핵심 로직 위주로 선별해. 보충 설명도 추가해.
3. 이미지 보존: 원문에 포함된 모든 이미지 링크(![](link) 또는 <img src=link>)는 관련된 개념 설명 바로 아래에 정확히 배치해.
4. 요약: 노트의 제일 마지막에 학습 내용을 다시 상기할 수 있게 내용 요약 섹션을 추가해줘.

### Constraints (제약 조건)
1. 계층 구조: Notion import에 최적화되도록 # (H1), ## (H2), ### (H3) 단계를 엄격히 지켜줘.
2. 노션 전용 포맷:
   - 핵심 개념/주의사항은 `> **💡 Tip**` 형식을 사용하여 콜아웃(Callout)으로 처리해.
   - 5줄 이상의 코드는 '코드 보기' 토글(Toggle)로 감싸줘.
3. 수식 처리: 모든 수학적 공식이나 변수는 Notion에서 렌더링 가능하도록 `$inline$` 또는 `$$display$$` (LaTeX) 형식을 사용해.
4. 언어: 모든 설명은 한국어로 작성하되, 기술 용어는 필요시 영어와 병기해.
5. 괄호 주의: 괄호가 열리면 반드시 닫는걸 잊지마!
6. 정리 내용 외에 추가로 답변은 금지!

### Input Data (Jupyter Notebooks)
{context}
"""

class StudyArchitect:
    def __init__(self, model_name="qwen/qwen3-32b"):
        # tempreature를 낮추어 정확한 답변이 나오도록 유도
        self.llm = ChatGroq(
            model = model_name,
            temperature= 0.2,
            top_p = 1,
            stream = False,
            stop = None,
            include_reasoning = False
        )
        
    def _build_context_string(self, parsed_data):
        """파싱된 데이터를 LLM이 이해하기 쉬운 텍스트 형식으로 변환합니다."""
        context_parts = []
        for nb in parsed_data:
            context_parts.append(f"--- Source File: {nb['filename']} ---")
            for cell in nb['cells']:
                context_parts.append(f"[{cell['type']}]")
                context_parts.append(cell['source'])
                if cell['images']:
                    context_parts.append(f"(Included Images: {', '.join(cell['images'])})")
            context_parts.append("-" * 30)
        return "\n".join(context_parts)

    def generate_notion_note(self, parsed_data):
        """RCTC 프레임워크를 기반으로 스터디 노트를 생성합니다."""
        
        # 1. 컨텍스트 스트링 생성
        context = self._build_context_string(parsed_data)
        
        # 2. RCTC 프레임워크 기반 프롬프트 설계
        template = PROMPT_TEMPLATE

        prompt = ChatPromptTemplate.from_template(template)
        
        # 3. 체인 생성 및 실행
        chain = prompt | self.llm | StrOutputParser()
        
        return chain.invoke({"context": context})
    