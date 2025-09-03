class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.5"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.5/dbfsharp-osx-arm64.tar.gz"
      sha256 "7cebf16a86f8e9f0022217f069a901800ab7c41b0d60bdfca75c7f2a421fddaa"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.5/dbfsharp-osx-x64.tar.gz"
      sha256 "58fc909e48805de6377f17cd57d8c6642e765b570841e93ad027956de6bc1f19"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.5/dbfsharp-linux-x64.tar.gz"
      sha256 "f052687c54c6d70fc7beb7a45022443db5c49f5c5d7676d77e8be4ee2a5070f8"
    end
  end

  def install
    bin.install "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end