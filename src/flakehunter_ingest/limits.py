MAX_ARTIFACT_ZIP_BYTES = 10 * 1024 * 1024  # compressed: listed size and downloaded size
MAX_REPORT_BYTES = 11 * 1024 * 1024  # 11,534,336: all XML in one artifact, decompressed
MAX_ZIP_ENTRIES = 1000  # files and directories


class ArtifactRejected(ValueError):
    """The artifact is refused for its size or shape. The message is fixed text, safe to log."""
