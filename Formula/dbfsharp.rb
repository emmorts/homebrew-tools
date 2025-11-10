class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.9"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.9/dbfsharp-osx-arm64.tar.gz"
      sha256 "a8078ad12d1dd3cfe10349bbd949cc676e0efb959001db4d41250ca96ecb3d4d"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.9/dbfsharp-osx-x64.tar.gz"
      sha256 "22756b7a857a518808a7a2956fb9093ee8d7c04a9100d599ca76515d3c78bd97"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.9/dbfsharp-linux-x64.tar.gz"
      sha256 "1c0db453ea7027b260593bed9d418d33a41fb454cb68c6a437f2e972f3126b2d"
    end
  end

  def install
    bin.install "DbfSharp.ConsoleAot" => "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end
