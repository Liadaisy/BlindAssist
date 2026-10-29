
import cv2
from pathlib import Path


class Camera:
    def __init__(self, source=0, source_type="camera"):
        self.cap = None

        if source_type == "youtube":
            self._open_youtube(str(source))

        elif source_type == "video":
            path = Path(str(source)).expanduser()
            if not path.is_file():
                raise FileNotFoundError(f"Video not found: {path}")
            self.cap = cv2.VideoCapture(str(path))

        elif source_type in ("camera", "stream"):
            self.cap = cv2.VideoCapture(source)

        else:
            raise ValueError(f"Unsupported input type: {source_type}")

        if self.cap is None or not self.cap.isOpened():
            self.release()
            raise RuntimeError(f"Cannot open input source: {source}")

    def _open_youtube(self, url):
        from cap_from_youtube import cap_from_youtube

        errors = []

        for resolution in ("720p", "480p", "360p", "240p"):
            candidate = None
            try:
                print(f"Trying YouTube resolution: {resolution}")
                candidate = cap_from_youtube(url, resolution)

                if candidate is not None and candidate.isOpened():
                    self.cap = candidate
                    print(f"YouTube stream opened at {resolution}")
                    return

                errors.append(f"{resolution}: stream unavailable")

            except Exception as exc:
                errors.append(f"{resolution}: {exc}")

            finally:
                if candidate is not None and candidate is not self.cap:
                    candidate.release()

        raise RuntimeError(
            "Could not open YouTube video:\n" + "\n".join(errors)
        )

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None

        success, frame = self.cap.read()
        if not success:
            return None

        return frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
