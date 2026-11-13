// Client-side PDF validation: a browser port of ecfiler/pdf/validator.py.
//
// Session 7 (2026-11-13). /validate used to POST the file to the API's
// /api/validate, which has been unreachable since July, so the free tool
// failed for every visitor. This runs the same checks in the browser with
// pdf.js; the file never leaves the visitor's machine. The messages are the
// Python validator's own wording so the two surfaces read the same.
//
// Mirrors validate_pdf(path, max_size_mb=100, check_pdfa=True):
//   extension, size limit, empty file, opens at all, password protection,
//   zero pages, encryption, AcroForm/XFA form fields, PDF/A identification
//   in the XMP metadata, searchable text in the first 5 pages (> 20 chars).
//
// One deliberate difference: Python suppresses the "encrypted" error when any
// warning was already raised (a side effect of reusing `warnings` for
// owner-only encryption). Here an encrypted file is always an error, which
// is what CM/ECF does with it.

export const MAX_SIZE_MB = 100;
const TEXT_PAGES = 5;
const MIN_TEXT_CHARS = 20;

export interface ValidationResult {
  valid: boolean;
  file_size_mb: number;
  page_count: number;
  has_text: boolean;
  is_encrypted: boolean;
  has_form_fields: boolean;
  is_pdfa: boolean | null;
  errors: string[];
  warnings: string[];
}

function result(partial: Partial<ValidationResult> & { file_size_mb: number; errors: string[] }): ValidationResult {
  return {
    valid: partial.errors.length === 0,
    page_count: 0,
    has_text: false,
    is_encrypted: false,
    has_form_fields: false,
    is_pdfa: null,
    warnings: [],
    ...partial,
  };
}

/** True when the XMP packet identifies the file as PDF/A (validator.py _check_pdfa_metadata). */
export function xmpSaysPdfA(xmp: string | null | undefined): boolean {
  if (!xmp) return false;
  return xmp.toLowerCase().includes("pdfaid") || xmp.includes("PDF/A");
}

export async function validatePdfInBrowser(file: File): Promise<ValidationResult> {
  const errors: string[] = [];
  const warnings: string[] = [];

  const dot = file.name.lastIndexOf(".");
  const ext = dot >= 0 ? file.name.slice(dot) : "";
  if (ext.toLowerCase() !== ".pdf") {
    errors.push(`File extension is '${ext}', expected '.pdf'`);
  }

  const sizeMb = file.size / (1024 * 1024);
  if (sizeMb > MAX_SIZE_MB) {
    errors.push(`File size ${sizeMb.toFixed(1)}MB exceeds ${MAX_SIZE_MB}MB limit`);
  }
  if (file.size === 0) {
    errors.push("File is empty (0 bytes)");
    return result({ file_size_mb: 0, errors });
  }

  const pdfjs = await import("pdfjs-dist");
  pdfjs.GlobalWorkerOptions.workerSrc = new URL(
    "pdfjs-dist/build/pdf.worker.min.mjs",
    import.meta.url
  ).toString();

  const task = pdfjs.getDocument({ data: await file.arrayBuffer() });
  let doc;
  try {
    doc = await task.promise;
  } catch (e) {
    const name = (e as { name?: string })?.name;
    if (name === "PasswordException") {
      errors.push("PDF is password-protected. CM/ECF does not accept encrypted PDFs.");
      await task.destroy();
      return result({ file_size_mb: sizeMb, is_encrypted: true, errors });
    }
    errors.push(`Cannot open PDF: ${(e as Error)?.message ?? String(e)}`);
    await task.destroy();
    return result({ file_size_mb: sizeMb, errors });
  }

  try {
    const pageCount = doc.numPages;
    if (pageCount === 0) {
      errors.push("PDF has zero pages.");
      return result({ file_size_mb: sizeMb, errors });
    }

    const { info, metadata } = await doc.getMetadata();
    const docInfo = (info ?? {}) as Record<string, unknown>;
    const isEncrypted = Boolean(docInfo.EncryptFilterName);
    let hasFormFields = false;
    if (docInfo.IsXFAPresent) {
      hasFormFields = true;
      warnings.push("PDF contains XFA form data. CM/ECF may reject it, so convert it to a static PDF first.");
    } else if (docInfo.IsAcroFormPresent) {
      hasFormFields = true;
      warnings.push("PDF contains fillable form fields. CM/ECF may reject it, so consider flattening.");
    }

    const isPdfA = xmpSaysPdfA(metadata?.getRaw?.() as string | undefined);
    if (!isPdfA) warnings.push("Not PDF/A conformant. Some courts prefer PDF/A.");

    if (isEncrypted) errors.push("PDF is encrypted. CM/ECF does not accept encrypted PDFs.");

    let hasText = false;
    try {
      for (let i = 1; i <= Math.min(TEXT_PAGES, pageCount); i++) {
        const page = await doc.getPage(i);
        const content = await page.getTextContent();
        const text = content.items.map((it) => ("str" in it ? it.str : "")).join(" ").trim();
        if (text.length > MIN_TEXT_CHARS) {
          hasText = true;
          break;
        }
      }
    } catch {
      warnings.push("Could not extract text, so the PDF may not be searchable.");
    }
    if (!hasText && errors.length === 0) {
      warnings.push("No searchable text detected. CM/ECF requires searchable PDFs. Consider running OCR (ocrmypdf).");
    }

    return result({
      file_size_mb: sizeMb,
      page_count: pageCount,
      has_text: hasText,
      is_encrypted: isEncrypted,
      has_form_fields: hasFormFields,
      is_pdfa: isPdfA,
      errors,
      warnings,
    });
  } finally {
    await task.destroy();
  }
}
