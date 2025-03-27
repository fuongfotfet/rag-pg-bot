def test_local_ocr_loader():
    from rag_system.components.loaders.local_loader import LocalOCRPDFLoader
    import os

    # Đường dẫn tới file PDF test (thay bằng file thật)
    test_pdf_path = "data/13nd.signed.pdf"  # ví dụ: "data/vb_scan_test.pdf"

    if not os.path.exists(test_pdf_path):
        print("❌ File PDF không tồn tại:", test_pdf_path)
        return

    loader = LocalOCRPDFLoader(dpi=300, lang="vie")
    chunks = loader.load(test_pdf_path)

    print(f"✅ Đã đọc {len(chunks)} trang từ file PDF.")
    for i, chunk in enumerate(chunks):
        print(f"\n--- Trang {chunk.page_number} (offset {chunk.offset}) ---")
        print(chunk.content[:500])  # in 500 ký tự đầu

if __name__ == "__main__":
    test_local_ocr_loader()
