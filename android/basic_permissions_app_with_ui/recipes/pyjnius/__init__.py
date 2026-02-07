from pythonforandroid.recipes.pyjnius import PyjniusRecipe
import os
import subprocess


class PyjniusRecipePinned(PyjniusRecipe):
    """
    Custom pyjnius recipe to fix Python 3.12 compatibility issue with 'long' type.
    """

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)

        # Path to the build directory
        build_dir = self.get_build_dir(arch.arch)
        jnius_dir = os.path.join(build_dir, 'jnius')

        if not os.path.exists(jnius_dir):
            print(f"Warning: {jnius_dir} not found, skipping patch")
            return

        # Patch all .pxi and .pyx files to replace long with int
        try:
            # Replace (int, long) with int
            subprocess.run(
                ['find', jnius_dir, '-type', 'f', '(', '-name', '*.pxi', '-o', '-name', '*.pyx', ')',
                 '-exec', 'sed', '-i', 's/(int, long)/int/g', '{}', ';'],
                check=False
            )

            # Replace isinstance(x, long) with isinstance(x, int)
            subprocess.run(
                ['find', jnius_dir, '-type', 'f', '(', '-name', '*.pxi', '-o', '-name', '*.pyx', ')',
                 '-exec', 'sed', '-i', r's/isinstance(\([^,]*\), long)/isinstance(\1, int)/g', '{}', ';'],
                check=False
            )

            # Remove dictionary entries like "long: 'J',"
            subprocess.run(
                ['find', jnius_dir, '-type', 'f', '-name', '*.pxi',
                 '-exec', 'sed', '-i', r'/^\s*long:\s*.*,\s*$/d', '{}', ';'],
                check=False
            )

            print(f"Successfully patched pyjnius files in {jnius_dir} for Python 3.12 compatibility")
        except Exception as e:
            print(f"Error patching pyjnius files: {e}")


recipe = PyjniusRecipePinned()
