{
  description = "MeepMRP packaged using poetry2nix";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication defaultPoetryOverrides;
      in
      {
        #packages = {
        #  xmpp-bridge-py = mkPoetryApplication {
        #    projectDir = self;
        #    overrides = defaultPoetryOverrides.extend
        #      (self: super: {
        #        xmpppy = super.xmpppy.overridePythonAttrs
        #        (
        #          old: {
        #            buildInputs = (old.buildInputs or [ ]) ++ [ super.setuptools ];
        #          }
        #        );
        #      });
        #    dependencies = [
        #      pkgs.coreutils
        #    ];
        #  };
        #  default = self.packages.${system}.xmpp-bridge-py;
        #};

        devShells.default = pkgs.mkShell {
          #inputsFrom = [ self.packages.${system}.xmpp-bridge-py ];
          buildInputs = [
            pkgs.bashInteractive
          ];
          packages = [
            pkgs.poetry
          ];
        };
      });
}
