import sys
import os
import matplotlib.pyplot as plt

# Add the Algorithm directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Algorithm'))

# Now you can import Alg from the Algorithm directory
import Alg as cipher

sbox_hex = cipher.SBOX

# Convert to decimal
SBOX_DEC = [int(x) for x in sbox_hex]

S = SBox(SBOX_DEC)

def save_pollock(mat,
                 color_scheme="CMRmap_r",
                 file_name="pollock",
                 vmin=0,
                 vmax=20,
                 folder=None,
                 frame=True,
                 visible_axes=True,
                 colorbar=True,
                 file_type="png"):
    import matplotlib.pyplot as plt
    fig, p = plt.subplots(figsize=(15,15))
    if isinstance(mat, list):
        abs_mat = [[abs(mat[i][j]) for j in range(0, len(mat[0]))]
                   for i in range(0, len(mat))]
    else:
        abs_mat = [[abs(mat[i][j]) for j in range(0, mat.ncols())]
                   for i in range(0, mat.nrows())]
    axes = p.imshow(
        abs_mat,
        interpolation="none",
        cmap = plt.colormaps.get_cmap(color_scheme).resampled(int(_sage_const_100))
        vmin=vmin,
        vmax=vmax,
    )
    if colorbar:
        fig.colorbar(axes, orientation='vertical', fraction=0.046, pad=0.04)
    p.set_aspect('equal')
    p.get_xaxis().set_visible(visible_axes)
    p.get_yaxis().set_visible(visible_axes)
    p.patch.set_alpha(0)
    p.set_frame_on(frame)
    if folder == None:
        name_base = "{}."+file_type
    else:
        name_base = folder + "/{}." + file_type
    fig.savefig(name_base.format(file_name))

def to_2d_list(lst, sublist_size):
    if sublist_size <= 0:
        raise ValueError("Sublist size must be greater than zero.")
    
    return [lst[i:i + sublist_size] for i in range(0, len(lst), sublist_size)]

if __name__ == "__main__":
    
    
    save_pollock(S.difference_distribution_table())