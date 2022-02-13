import argparse
from pathlib import Path
from requests_html import HTMLSession
import cairosvg

def dump_item(item_id, item_metadata, item_svg, args):
    output_dir = Path(args.output_dir)
    (output_dir / f'{item_id}.json').write_text(item_metadata)
    (output_dir / f'{item_id}.svg').write_text(item_svg)
    output_png_path = str(output_dir/f'{item_id}.png')
    cairosvg.svg2png(bytestring=item_svg, write_to=output_png_path)

def main(args):
    session = HTMLSession()
    r = session.get(args.url)
    r.html.render()
    for item in r.html.find(".pedagogy-item"):
        item_id = item.attrs['id']
        item_metadata = item.attrs['data-metadata']
        item_svg = item.find("svg")[0].html
        dump_item(item_id, item_metadata, item_svg, args)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument("--url", default='http://0.0.0.0:8000/acpedagogy_examples.html')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)