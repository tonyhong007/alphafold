# Commented out IPython magic to ensure Python compatibility.
# Set environment variables before running any other code.
import os
os.environ['TF_FORCE_UNIFIED_MEMORY'] = '1'
os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = '4.0'

#@title 1. Install third-party software

#@markdown Please execute this cell by pressing the _Play_ button
#@markdown on the left to download and import third-party software
#@markdown in this Colab notebook. (See the [acknowledgements](https://github.com/deepmind/alphafold/#acknowledgements) in our readme.)

#@markdown **Note**: This installs the software on the Colab
#@markdown notebook in the cloud and not on your computer.

from IPython.utils import io
import os
import subprocess
import tqdm.notebook

TQDM_BAR_FORMAT = '{l_bar}{bar}| {n_fmt}/{total_fmt} [elapsed: {elapsed} remaining: {remaining}]'

try:
  with tqdm.notebook.tqdm(total=100, bar_format=TQDM_BAR_FORMAT) as pbar:
    with io.capture_output() as captured:
      # Uninstall default Colab version of TF.
      os.system("pip uninstall -y tensorflow")

      os.system("sudo apt install --quiet --yes hmmer")
      pbar.update(6)

      # Install py3dmol.
      os.system("pip install py3dmol")
      pbar.update(2)

      # Install OpenMM and pdbfixer.
      os.system("rm -rf /opt/conda")
      os.system("wget -q -P /tmp https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && bash /tmp/Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda && rm /tmp/Miniconda3-latest-Linux-x86_64.sh")
      pbar.update(9)

      path = os.environ['PATH']
      new_path = f"/opt/conda/bin:{path}"
      os.environ['PATH'] = new_path
      os.system("conda install -qy conda==4.13.0 && conda install -qy -c conda-forge python=3.9 openmm=7.5.1 pdbfixer")
      pbar.update(80)

      # Create a ramdisk to store a database chunk to make Jackhmmer run fast.
      os.system("sudo mkdir -m 777 --parents /tmp/ramdisk")
      os.system("sudo mount -t tmpfs -o size=9G ramdisk /tmp/ramdisk")
      pbar.update(2)

      os.system("wget -q -P /content https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt")
      pbar.update(1)
except subprocess.CalledProcessError:
  print(captured)
  raise

# Commented out IPython magic to ensure Python compatibility.
#@title 2. Download AlphaFold

#@markdown Please execute this cell by pressing the *Play* button on
#@markdown the left.

GIT_REPO = 'https://github.com/deepmind/alphafold'
SOURCE_URL = 'https://storage.googleapis.com/alphafold/alphafold_params_colab_2022-12-06.tar'
PARAMS_DIR = './alphafold/data/params'
PARAMS_PATH = os.path.join(PARAMS_DIR, os.path.basename(SOURCE_URL))

try:
  with tqdm.notebook.tqdm(total=100, bar_format=TQDM_BAR_FORMAT) as pbar:
    with io.capture_output() as captured:
      os.system("rm -rf alphafold")
      os.system(f"git clone --branch main {GIT_REPO} alphafold")
      pbar.update(8)
      # Install the required versions of all dependencies.
      os.system("pip3 install -r ./alphafold/requirements.txt")
      # Run setup.py to install only AlphaFold.
      os.system("pip3 install --no-dependencies ./alphafold")
      os.system("pip3 install --upgrade pyopenssl")
      pbar.update(10)

      # Apply OpenMM patch.
      os.system("pushd /opt/conda/lib/python3.9/site-packages/ && patch -p0 < /content/alphafold/docker/openmm.patch && popd")

      # Make sure stereo_chemical_props.txt is in all locations where it could be searched for.
      os.system("mkdir -p /content/alphafold/alphafold/common")
      os.system("cp -f /content/stereo_chemical_props.txt /content/alphafold/alphafold/common")
      os.system("mkdir -p /opt/conda/lib/python3.9/site-packages/alphafold/common/")
      os.system("cp -f /content/stereo_chemical_props.txt /opt/conda/lib/python3.9/site-packages/alphafold/common/")

      # Load parameters
      os.system(f'mkdir --parents "{PARAMS_DIR}"')
      os.system(f'wget -O "{PARAMS_PATH}" "{SOURCE_URL}"')
      pbar.update(27)

      os.system(f'tar --extract --verbose --file="{PARAMS_PATH}" --directory="{PARAMS_DIR}" --preserve-permissions')
      os.system(f'rm "{PARAMS_PATH}"')
      pbar.update(55)
except subprocess.CalledProcessError:
  print(captured)
  raise