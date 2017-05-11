class PositionedAtom:
    def __init__(self, element, x, y, z, Z_part):
        self._element = element
        self._x = x
        self._y = y
        self._z = z
        self._Z_part = Z_part

    def get_element(self):
        return self._element

    def get_x(self):
        return self._x

    def get_y(self):
        return self._y

    def get_z(self):
        return self._z

    def get_Z_part(self):
        return self._Z_part
    
    def get_Z(self):
        if self._element == "C":
            return 6.0
        elif self._element == "H":
            return 1.0
        elif self._element == "O":
            return 8.0
        elif self._element == "N":
            return 7.0
        elif self._element == "F":
            return 9.0
        else:
            return None


class Molecule:
    def __init__(self):
        pass

    def get_n_a(self):
        return self._n_a

    def get_model(self):
        return self._model

    def get_property(self, name):
        return self._props[name]

    def get_atom(self, index):
        return self._atoms[index]

    def get_freq_count(self):
        return len(self._freqs)

    def get_freq(self, index):
        return self._freqs[index]

    def get_SMILES(self):
        return self._SMILES

    @staticmethod
    def from_xyz(xyz):
        m = Molecule()
        lines = xyz.split("\n")

        # Line 1 (number of atoms)
        m._n_a = int(lines[0])

        # Line 2
        props = lines[1].split("\t")
        m._props = dict()
        m._props["id"] = props[0] # String identifier
        m._props["A"] = float(props[1].replace("*^", "E")) # A (GHz) - Rotational constant
        m._props["B"] = float(props[2].replace("*^", "E")) # B (GHz) - Rotational constant
        m._props["C"] = float(props[3].replace("*^", "E")) # C (GHz) - Rotational constant
        m._props["mu"] = float(props[4].replace("*^", "E")) # mu (D) - Dipole moment
        m._props["alpha"] = float(props[5].replace("*^", "E")) # alpha (a_0^3) - Isotropic polarizability
        m._props["epsilon_HOMO"] = float(props[6].replace("*^", "E")) # epsilon_HOMO (Ha) - Energy of HOMO
        m._props["epsilon_LUMO"] = float(props[7].replace("*^", "E")) # epsilon_LUMO (Ha) - Energy of LUMO
        m._props["epsilon_gap"] = float(props[8].replace("*^", "E")) # epsilon_gap (Ha) - Energy gap
        m._props["R2"] = float(props[9].replace("*^", "E")) # R^2 (a_0^2) - Electronic spatial extent
        m._props["zpve"] = float(props[10].replace("*^", "E")) # zpve (Ha) - Zero point vibrational energy
        m._props["U_0"] = float(props[11].replace("*^", "E")) # U_0 (Ha) - Internal energy at 0K
        m._props["U"] = float(props[12].replace("*^", "E")) # U (Ha) - Internal energy at 298.15K
        m._props["H"] = float(props[13].replace("*^", "E")) # H (Ha) - Enthalpy at 298.15K
        m._props["G"] = float(props[14].replace("*^", "E")) # G (Ha) - Free energy at 298.15K
        m._props["C_v"] = float(props[15].replace("*^", "E")) # C_v (cal/molK) - Heat capacity at 298.15K

        m._atoms = []
        for i in range(2, m._n_a+2):
            xyz_props = lines[i].split("\t")
            element = xyz_props[0] # element symbol
            x = float(xyz_props[1].replace("*^", "E")) # x (angstrom) - X coordinate
            y = float(xyz_props[2].replace("*^", "E")) # y (angstrom) - Y coordinate
            z = float(xyz_props[3].replace("*^", "E")) # z (angstrom) - Z coordinate
            Z_part = float(xyz_props[4].replace("*^", "E")) # Z_part (e) - Mulliken partial charge 
            m._atoms.append(PositionedAtom(element, x, y, z, Z_part))

        freq_props = lines[m._n_a+2].split("\t")
        m._freqs = [float(freq_prop.replace("*^", "E")) for freq_prop in freq_props]
        m._SMILES = lines[m._n_a+3]

        return m

    @staticmethod
    def from_xyz_file(file_path):
        xyz = None
        with open(file_path, 'r') as content_file:
             xyz = content_file.read()
        return Molecule.from_xyz(xyz)

