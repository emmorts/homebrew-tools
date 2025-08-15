class Dbfsharp < Formula
  desc "High-performance .NET library and CLI tool for reading dBASE (DBF) files"
  homepage "https://github.com/emmorts/dbfsharp"
  version "0.2.3"
  license "MIT"

  on_macos do
    on_arm do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.3/dbfsharp-osx-arm64.tar.gz"
      sha256 "0b810de252b0531800ee8f1e0037c65bae8de161653729b6d0f2f9ae5845014f"
    end
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.3/dbfsharp-osx-x64.tar.gz"
      sha256 "7588a1949e8907afeacd4c8b6f1f3330e4917d1f0a08c659bcd522be2fd0b4b3"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/emmorts/dbfsharp/releases/download/v0.2.3/dbfsharp-linux-x64.tar.gz"
      sha256 "ebf7606a29618d8cfd2a4e77d8e68edb83f7379291bacb45109040334963e945"
    end
  end

  def install
    bin.install "dbfsharp"
  end

  test do
    system "#{bin}/dbfsharp", "--help"
  end
end