// Local macOS Vision OCR. No network, account, generated text or normalization.
import Foundation
import PDFKit
import Vision
import AppKit
let args=CommandLine.arguments
guard args.count==3, let doc=PDFDocument(url:URL(fileURLWithPath:args[1])), let limit=Int(args[2]) else { exit(2) }
guard doc.pageCount<=250 else { exit(3) }
for i in 0..<min(doc.pageCount,limit) {
    guard let page=doc.page(at:i) else {continue}
    let image=page.thumbnail(of:NSSize(width:1800,height:2400),for:.mediaBox)
    guard let cg=image.cgImage(forProposedRect:nil,context:nil,hints:nil) else {continue}
    let request=VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection=false
    request.recognitionLanguages=["en-US"]
    do {
        try VNImageRequestHandler(cgImage:cg,options:[:]).perform([request])
        let rows=(request.results ?? []).sorted {
            if abs($0.boundingBox.midY-$1.boundingBox.midY)>0.008 {return $0.boundingBox.midY>$1.boundingBox.midY}
            return $0.boundingBox.minX<$1.boundingBox.minX
        }
        print("\n[ORIGINAL PDF PAGE \(i+1), MACHINE OCR; VERIFY TABLE COLUMNS IN SOURCE]\n")
        for row in rows {if let value=row.topCandidates(1).first {print(value.string)}}
    } catch {fputs("OCR_PAGE_UNAVAILABLE\n",stderr)}
}
