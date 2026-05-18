import os
import re
import fitz

def setup_folders():
    """데이터가 들어갈 서랍장을 깨끗하게 만듭니다."""
    os.makedirs("database/math", exist_ok=True)
    os.makedirs("images", exist_ok=True)

def process_pdfs():
    input_dir = "inputs"
    if not os.path.exists(input_dir):
        return

    pdf_files = [f for f in os.listdir(input_dir) if f.endswith(".pdf")]
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        doc = fitz.open(pdf_path)
        base_name = os.path.splitext(pdf_file)[0]

        print(f"[{pdf_file}] 문항별 정밀 분리 시작...")

        global_question_idx = 1

        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            # [핵심 가위질 규칙] 
            # 줄바꿈(\n) 뒤에 숫자(\d+)와 마침표(\.)가 오는 패턴을 기준으로 텍스트를 통째로 쪼갭니다.
            questions = re.split(r'\n(?=\d+\.)', page_text)
            
            # 해당 페이지에 포함된 도형/이미지 목록 추출
            image_list = page.get_images(full=True)
            image_md_links = ""
            
            for img_idx, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                # 이미지 추출 시 현재 페이지의 첫 문제 인덱스를 활용하여 고유한 이름을 생성합니다.
                img_name = f"{base_name}_q{global_question_idx}_{img_idx}.{image_ext}"
                img_path = os.path.join("images", img_name)
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                image_md_links += f"\n![도형](images/{img_name})\n"

            # 쪼개진 문제들을 하나씩 정돈된 파일로 저장
            is_first_on_page = True
            for q_text in questions:
                q_text_stripped = q_text.strip()
                if not q_text_stripped:
                    continue
                
                # [수정/보완] 첫 번째 조각에 시험지 타이틀이나 페이지 헤더 등 문제 번호로 시작하지 않는
                # 노이즈/헤더 텍스트가 있을 경우, 이를 빈 문제로 오인하여 번호가 밀리는 현상을 방지합니다.
                if not re.match(r'^\d+\.', q_text_stripped):
                    print(f"-> 헤더/노이즈 텍스트 감지 및 제외: {q_text_stripped[:30]}...")
                    continue
                
                # 파일명이 꼬이지 않도록 고유한 문제 번호를 부여하여 서랍에 넣습니다.
                # [수정/보완] global_question_idx == 1 일 때만 이미지를 붙이면 2페이지 이후의 이미지가 유실되므로,
                # 각 페이지의 첫 번째 문항(is_first_on_page)에 해당 페이지의 이미지들을 매핑해 줍니다.
                md_content = f"""---
id: {base_name}_q{global_question_idx}
subject: 수학
source: {pdf_file}
page: {page_num + 1}
---

# {global_question_idx}번 문제
{q_text_stripped}

{image_md_links if is_first_on_page else ""} 
"""
                output_md_path = f"database/math/{base_name}_q{global_question_idx}.md"
                with open(output_md_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                global_question_idx += 1
                is_first_on_page = False

        doc.close()

if __name__ == "__main__":
    setup_folders()
    process_pdfs()
