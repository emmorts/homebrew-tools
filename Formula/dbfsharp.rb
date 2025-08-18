class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.4"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.4/dbfsharp-osx-arm64.tar.gz"
      sha256 "362caf11da0da812d8ed6b4a2c07e31750302edcca1c24de3f343fbd65e8dfd8"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.4/dbfsharp-osx-x64.tar.gz"
      sha256 "27da22d7bd85fcf2d458881801a1a35dd4ed55a13d2b82867073f029897c340a"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.4/dbfsharp-linux-x64.tar.gz"
      sha256 "712dd63b93902fdfe327039047a95434d3009d6f3118875ef5c5f10e08a5e035"
    end
  end

  def install
    bin.install "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end