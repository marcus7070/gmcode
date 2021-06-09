{
  description = "Python helper for writing gcode";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    # pygcode.url = "github:marcus7070/pygcode";
  };

  outputs = { self, nixpkgs, flake-utils, ... } @inputs :
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
        python = pkgs.python3.override {
          packageOverrides = py-self: py-super: {

            gmcode = py-self.buildPythonPackage rec {

              pname = "gmcode";
              version = "0.1";
              src = ./.;

              propagatedBuildInputs = with py-self; [ attrs pygcode ];

              checkInputs = with py-self; [ pytestCheckHook mypy ];
              pytestFlagsArray = [ "-vv" ];

            };

            # can't figure out how to compose python packageOverrides, so just cut and paste:
            pygcode = py-self.buildPythonPackage {

              pname = "pygcode";
              version = "202106";
              src = pkgs.fetchFromGitHub {
                owner = "marcus7070";
                repo = "pygcode";
                rev = "29dd5a51067302287e9f6be954416f68741c4354";
                sha256 = "sha256-GPzLPWg6TrypzfExZq7rrF3Wcj9bll4XP9cc5ZlEmFA=";
              };
              
              propagatedBuildInputs = with py-self; [
                euclid3
                six
              ];

              checkPhase = ''
                cd tests
                ${python.interpreter} -m unittest discover -s . -p 'test_*.py' --verbose
              '';

              pythonImportsCheck = [ "pygcode" ];

            };

            euclid3 = py-self.buildPythonPackage rec {

              pname = "euclid3";
              version = "0.01";

              src = py-self.fetchPypi {
                inherit pname version;
                sha256 = "sha256-JbgnpXrb/Zo/qGJeQ6vD6Qf2HeYiND5+U4SC75tG/Qs=";
              };

              pythonImportsCheck = [ "euclid3" ];

              meta = with pkgs.lib; {
                description = "2D and 3D maths module for Python";
                homepage = "https://pypi.org/project/euclid3/";
                license = licenses.lgpl21;
                maintainers = with maintainers; [ marcus7070 ];
              };
            };

          };
          self = python;
        };
      in rec {
        defaultPackage = python.withPackages (ps: [ ps.gmcode ] );
        devShell = pkgs.mkShell { buildInputs = [ (python.withPackages (ps: with ps; [
          pytest
          pytest-xdist
          mypy
          black
          attrs
          pygcode
        ] )) ]; };
      }
    );
}
