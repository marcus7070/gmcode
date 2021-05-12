{
  description = "Python helper for writing gcode";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in rec {
        packages.gmcode = pkgs.python3.pkgs.buildPythonPackage rec {
          pname = "gmcode";
          version = "0.1";
          src = ./.;

          buildInputs = with pkgs.python3.pkgs; [ attrs ];

          checkInputs = with pkgs.python3.pkgs; [ pytestCheckHook ];
        };
        defaultPackage = pkgs.python3.withPackages (_: [ packages.gmcode ] );
      }
    );
}
