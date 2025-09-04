class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.6"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-osx-arm64.tar.gz"
      sha256 "d485231742f63ec0b2792ea31a437c8c518b2c5510c64be947db76339bc5670a"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-osx-x64.tar.gz"
      sha256 "2d4e6df6be1cdd1b84325b28e03fec5a81bb2613714e007dd31850ccf09d8c29"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-linux-x64.tar.gz"
      sha256 "1634c4b57736873f053398804d26203f25cd654e7b58db12b8ca2f5555ecb9b4"
    end
  end

  def install
    bin.install "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end