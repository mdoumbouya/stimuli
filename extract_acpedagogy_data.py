import argparse
from pathlib import Path
from requests_html import HTMLSession
import cairosvg
import numpy as np
import json

vector_spaces = ['concept_vector', 'context_vector', 'context_vector_inclusive']

def dump_item(item_metadata, item_vectors, item_svg, args):
    output_dir = Path(args.output_dir)
    item_id = item_metadata['id']
    # dump svg
    (output_dir / f'{item_id}.svg').write_text(item_svg)

    # dump png
    output_png_path = str(output_dir/f'{item_id}.png')
    cairosvg.svg2png(bytestring=item_svg, write_to=output_png_path)

    # dump metadata
    (output_dir / f'{item_id}.json').write_text(
        json.dumps(item_metadata)
    )

    # dump vectors
    for vector_name in vector_spaces:
        vector_path = output_dir / f'{item_id}_{vector_name}.vec.txt'
        vector = np.array(item_vectors[vector_name])
        np.savetxt(
            vector_path,
            vector
        )


def dump_all(all_metadata, all_vectors, args):
    output_dir = Path(args.output_dir)
    # dump svg
    (output_dir / f'metadata.json').write_text(
        json.dumps(all_metadata)
    )
    for vs in vector_spaces:
        vector_path = output_dir / f'vectors_{vs}.vec.txt'
        np.savetxt(
            vector_path,
            all_vectors[vs]
        )


def main(args):
    session = HTMLSession()
    r = session.get(args.url)
    r.html.render(timeout = 2000)
    all_metadata = []
    all_vectors = {vs: [] for vs in vector_spaces}
    for item_id, item in enumerate(r.html.find(".pedagogy-item")):
        item_metadata = json.loads(item.attrs['data-metadata'])
        item_metadata['name'] = item.attrs['id']
        item_metadata['id'] = f"{item_id:05d}"
        item_vectors = json.loads(
            item.attrs['data-vectors']
        )
        item_svg = item.find("svg")[0].html
        all_metadata.append(
            item_metadata
        )
        for vs in vector_spaces:
            all_vectors[vs].append(
                np.array(item_vectors[vs])
            )
        dump_item(item_metadata, item_vectors, item_svg, args)
    dump_all(all_metadata, all_vectors, args)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir")
    parser.add_argument(
        "--url", default='http://0.0.0.0:8000/acpedagogy_examples.html')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    main(args)
