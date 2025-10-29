import argparse
import collada
import fast_simplification
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load and visualize a 3D mesh file.')
    parser.add_argument('file_path', type=str, help='Path to the mesh file to inspect.')
    args = parser.parse_args()
    print(args.file_path)

    input_path = Path(args.file_path)
    output_name = f"{input_path.stem}_Collision.DAE"
    output_path = f"{input_path.parts[0]}/collision/{output_name}"
    print(output_path)

    mesh = collada.Collada(str(input_path))
    print(f"File {str(input_path)} loaded successfully. Number of geometries: {len(mesh.geometries)}")

    # clear unwanted libraries
    print("Clearing materials, effects, lights, and cameras...")
    mesh.effects.clear()
    mesh.materials.clear()
    mesh.lights.clear()
    mesh.cameras.clear()

    for geom in mesh.geometries:
        print(geom.id)
        print(geom.sourceById)
        for primitive in list(geom.primitives):
            print("Before simplification")
            print(primitive.vertex.shape)
            print(primitive.vertex_index.shape)
            points_out, faces_out = fast_simplification.simplify(primitive.vertex, primitive.vertex_index, 0.5)
            print("After simplification")
            print(points_out.shape)
            print(faces_out.shape)

    mesh.write(str(output_path))
    print(f"Save clean mesh to: {output_path}")

