# Maintainer: Duvet05 <gonzalo.galvezc@pucp.edu.pe>
_pkgname=web-blocker
pkgname=web-blocker
pkgver=1.0
pkgrel=1
pkgdesc="A tool to block unwanted websites using iptables"
arch=('any')
url="https://github.com/Duvet05/web-blocker"
license=('GPL3')
depends=('bash' 'iptables' 'python3' 'python-dnspython')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('1825b5486207a781f4b6f8f27e4dd7a6786d1853c7870bcad5c4d3774dabd7cc')

package() {
    install -Dm755 "$srcdir/web-blocker.sh" "$pkgdir/usr/bin/web-blocker"
    install -Dm755 "$srcdir/web-blocker.py" "$pkgdir/usr/lib/web-blocker/web-blocker.py"
    install -Dm644 "$srcdir/sites.conf" "$pkgdir/etc/web-blocker/sites.conf"
    install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
}