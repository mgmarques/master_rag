import json

from pathlib import Path
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered


def process_pdf_worker(file_path, config_dict, target_root):
    """
    This function is now in a physical file,
    so multiprocessing can import it correctly.
    """
    try:
        file = Path(file_path)
        config_parser = ConfigParser(config_dict)

        # Models are loaded inside the process
        converter = PdfConverter(
            artifact_dict=create_model_dict(),
            config=config_parser.generate_config_dict(),
            llm_service=config_parser.get_llm_service(),
        )

        rendered = converter(str(file))
        markdown, metadata, images = text_from_rendered(rendered)

        file_target_dir = Path(target_root) / file.stem
        file_target_dir.mkdir(parents=True, exist_ok=True)

        (file_target_dir / f"{file.stem}.md").write_text(markdown, encoding="utf-8")

        for filename, img in images.items():
            img.save(file_target_dir / filename)

        metadata_dict = rendered.metadata if len(metadata) < 3 else metadata
        with open(file_target_dir / f"{file.stem}_metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata_dict, f, indent=4, ensure_ascii=False)

        return f"✅ {file.name}"
    except Exception as e:
        return f"❌ {Path(file_path).name}: {e}"
