# Maintainer: Duvet05 <gonzalo.galvezc@pucp.edu.pe>
_pkgname=web-blocker
pkgname=web-blocker
pkgver=1.0
pkgrel=1
pkgdesc="A tool to block websites locally and via network using /etc/hosts, iptables, and ufw"
arch=('any')
url="https://github.com/Duvet05/web-blocker"
license=('GNU')
depends=('bash' 'iptables' 'python3')
optdepends=('ufw: for additional firewall blocking')
source=("$pkgname-$pkgver.tar.gz")
sha256sums=('a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6')

package() {
    install -Dm755 "$srcdir/web-blocker.sh" "$pkgdir/usr/bin/web-blocker"
    install -Dm755 "$srcdir/web-blocker.py" "$pkgdir/usr/lib/web-blocker/web-blocker.py"
    install -Dm644 "$srcdir/sites.conf" "$pkgdir/etc/web-blocker/sites.conf"
    install -Dm644 "$srcdir/README.md" "$pkgdir/usr/share/doc/$pkgname/README.md"
}