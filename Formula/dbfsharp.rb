class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.6"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-osx-arm64.tar.gz"
      sha256 "d55090ad030b6d9f9f71c528696feca717436b3a9b6b21faf6f783cd42d12acb"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-osx-x64.tar.gz"
      sha256 "856bb55a9422ebb8c88e18fec174d8c6f2bade959eb2084409e6c61d350321e1"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.6/dbfsharp-linux-x64.tar.gz"
      sha256 "af3a6cedd89331bc9e82b5fd882832036e160c8c23eac06444fd9353b7bfcf0e"
    end
  end

  def install
    bin.install "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end