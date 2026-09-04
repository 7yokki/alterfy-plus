# Alterfy+

**Alterfy+**, YouTube kaynaklı müzik keşfini masaüstünde daha kontrollü, kişisel ve taşınabilir bir deneyime dönüştüren Alterfy yeniden yazımıdır. PyQt6 arayüzü, VLC oynatma motoru ve yt-dlp veri kaynağı korunur; ancak native araçlar işletim sistemi ve CPU mimarisine göre `tools/<platform>-<arch>/` altından çözülür.

> Alterfy+ çevrim içi kaynakları oynatmak için YouTube altyapısını kullanır. İçeriklerin indirilmesi ve kullanımı, ilgili platformun şartlarına ve telif hukukuna uygun olmalıdır.

## Alterfy+ ile gelenler

- **Portable runtime:** Windows x64/ARM64, Linux x64/ARM64 ve macOS x64/ARM64 hedefleri için VLC, yt-dlp ve isteğe bağlı ffmpeg klasör düzeni.
- **Gelişmiş ses:** Canlı VLC equalizer, bass boost, preamp, tiz ve `-14 LUFS` hedefli akıllı ses eşitleme filtresi.
- **Çevrim dışı kütüphane çekirdeği:** yt-dlp standalone binary ile video veya playlist indirme; dosyalar `~/.alterfy-plus/offline` altında tutulur.
- **Sanatçı ayrımı:** Kullanıcı sorgusu normalize edilir; Wikipedia REST API'den yerel önbelleğe sanatçı adı, açıklama, görsel ve sayfa bağlantısı alınır.
- **Yerel öneriler:** Dinleme geçmişi, sanatçı yakınlığı, tür ve tekrar cezasını açıklanabilir bir skorla birleştirir.
- **Arama önerileri:** Geçmiş sorgulardan hızlı, çevrim dışı öneriler.
- **Playlist taşıma:** YouTube playlist URL'si `OfflineService.import_playlist` ile taşınabilir.
- **Mevcut Alterfy özellikleri:** Senkron sözler, çoklu dil, playlist yönetimi, global medya tuşları ve asenkron yt-dlp araması.

## Kurulum

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Geliştirme sırasında native araçlar PATH üzerinden bulunabilir. Portable çalışma için ilgili klasörleri oluşturun:

```text
tools/
  windows-x64/       # vlc(.exe), yt-dlp(.exe), ffmpeg(.exe)
  windows-arm64/
  linux-x64/
  linux-arm64/
  macos-x64/
  macos-arm64/
```

`portable_manifest.json`, desteklenen hedefleri ve dağıtım lisansı notlarını içerir. VLC ve ffmpeg dağıtılırken kendi resmi lisans ve yeniden dağıtım koşulları korunmalıdır.

## Windows portable EXE

PowerShell'i proje kökünde açın:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\build_windows.ps1 -Arch x64
```

Betik PyInstaller ile `dist/AlterfyPlus/` klasörünü üretir. Resmi VLC runtime/plugins, yt-dlp.exe ve isteğe bağlı ffmpeg.exe dosyaları `tools\\windows-x64\\` içine konulmalıdır. Bu klasör tek başına taşınabilir dağıtım olarak zip'lenebilir.

## Mimari

| Katman | Sorumluluk |
|---|---|
| `main.py` | PyQt6 ekranları, arama, kuyruk ve VLC oynatma |
| `platform_tools.py` | Platform/mimari tespiti ve bundled tool çözümleme |
| `audio_engine.py` | Equalizer profili, bass boost, loudness normalizasyonu ve WAV ölçümü |
| `offline.py` | Portable yt-dlp ile indirme ve playlist taşıma |
| `artist_profiles.py` | Wikipedia tabanlı sanatçı profili ve yerel cache |
| `recommendations.py` | Yerel geçmişten öneri ve arama önerisi skoru |
| `data_manager.py` | `~/.alterfy-plus` kalıcı kullanıcı verisi |
| `lyrics.py` | lrclib senkron/plain sözler |

## Test

```bash
pytest -q
```

## Lisans

Projenin lisans metni `LICENSE` dosyasındadır. VLC, yt-dlp, ffmpeg ve uzak veri servislerinin kendi lisansları ayrıca geçerlidir.
