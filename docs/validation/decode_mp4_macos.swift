import Foundation
import AVFoundation
let asset = AVURLAsset(url: URL(fileURLWithPath: CommandLine.arguments[1]))
let reader = try AVAssetReader(asset: asset)
let video = AVAssetReaderTrackOutput(track: asset.tracks(withMediaType: .video)[0], outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_420YpCbCr8BiPlanarVideoRange])
let audio = AVAssetReaderTrackOutput(track: asset.tracks(withMediaType: .audio)[0], outputSettings: [AVFormatIDKey: kAudioFormatLinearPCM])
reader.add(video); reader.add(audio)
guard reader.startReading() else { fatalError("Cannot start: \(String(describing: reader.error))") }
var v=0; var a=0
while reader.status == .reading {
 let vb=video.copyNextSampleBuffer(); let ab=audio.copyNextSampleBuffer()
 if vb != nil {v += 1}; if ab != nil {a += 1}
 if vb == nil && ab == nil {break}
}
print("videoFrames=\(v) audioBuffers=\(a) status=\(reader.status.rawValue) error=\(String(describing: reader.error))")
guard reader.status == .completed && v == 1080 && a > 0 else {exit(1)}
