TDS Virtual Teaching Assistant 🤖
This is an intelligent assistant built for IIT Madras’ Tools in Data Science (TDS) Jan–Apr 2025 course. It can automatically answer student queries using semantic search over:

📝 Course notes (TDS_Notes.pdf, chunked + embedded)

💬 Discourse posts (from Jan to Apr 2025)

🖼️ Image input (OCR) — supports screenshots of questions

✨ Powered by Gradio + Sentence Transformers + OCR + fallback logic.

🚀 Try It Live
👉 Launch TDS Virtual TA on Hugging Face

💡 Features
✅ Accepts text or screenshot image questions
✅ Uses OCR (via Tesseract) for handwritten/image queries
✅ Finds top semantic matches using sentence embeddings
✅ Provides relevant lines, not just full paragraphs
✅ Includes fallback keyword search if semantic fails
✅ Returns source Discourse or course links for reference

🛠️ Tech Stack
Component	Library
UI & API	Gradio
Embeddings	sentence-transformers (all-MiniLM-L6-v2)
OCR	pytesseract + Pillow
Similarity	cosine_similarity from scikit-learn
Hosting	Hugging Face Spaces (Gradio SDK)
