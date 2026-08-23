import re
import os

def split_doc():
    file_path = r"C:\GitDev\apexai-os-meta\apex-meta\AI-Snippets\TO Split Doc_ DELTE.md"
    output_dir = r"C:\GitDev\apexai-os-meta\apex-meta\AI-Snippets"
    
    if not os.path.exists(file_path):
        print(f"Error: Source file {file_path} not found.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Pattern to match headers like "# R1 — Title"
    pattern = re.compile(r"^#\s+(R\d+)\s*[—-]\s*(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(content))
    
    if not matches:
        print("Error: No section headers matching '# R<number> — <Title>' found.")
        return
        
    print(f"Found {len(matches)} sections to split.")
    
    for i, match in enumerate(matches):
        r_id = match.group(1)      # e.g., "R1"
        r_title = match.group(2)   # e.g., "Karakeep → IPOS integration"
        
        # Clean title for filename
        clean_title = r_title
        clean_title = clean_title.replace("→", "to")
        clean_title = clean_title.replace("->", "to")
        clean_title = clean_title.replace(":", "")
        clean_title = clean_title.replace("+", "and")
        clean_title = clean_title.replace("?", "")
        clean_title = re.sub(r"[^\w\s-]", "", clean_title) # remove punctuation
        clean_title = re.sub(r"\s+", "_", clean_title.strip()) # replace spaces with underscores
        
        filename = f"{r_id}_{clean_title}.md"
        out_path = os.path.join(output_dir, filename)
        
        # Determine the start and end character indices for this section's text
        start_idx = match.end()
        end_idx = matches[i+1].start() if i + 1 < len(matches) else len(content)
        section_text = content[start_idx:end_idx]
        
        # Find content between the first ``` and the last ```
        first_tick = section_text.find("```")
        if first_tick != -1:
            next_nl = section_text.find("\n", first_tick)
            last_tick = section_text.rfind("```")
            if last_tick > next_nl:
                prompt_content = section_text[next_nl+1:last_tick].strip()
                with open(out_path, "w", encoding="utf-8") as out_f:
                    out_f.write(prompt_content + "\n")
                print(f"Successfully wrote: {filename}")
            else:
                print(f"Error: Mismatched backticks in section {r_id}")
        else:
            print(f"Warning: No code block found in section {r_id}")

if __name__ == "__main__":
    split_doc()
