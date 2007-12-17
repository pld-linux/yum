Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.2.8
Release:	2
License:	GPL
Group:		Applications/System
Source0:	http://linux.duke.edu/projects/yum/download/3.2/%{name}-%{version}.tar.gz
# Source0-md5:	25362cf7c9baeb557975be8ca2534555
Source1:	%{name}-pld-source.repo
Source2:	%{name}-updatesd.init
Patch0:		%{name}-missingok.patch
Patch1:		%{name}-obsoletes.patch
Patch2:		%{name}-chroot.patch
URL:		http://linux.duke.edu/projects/yum/
BuildRequires:	gettext-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
Requires:	python >= 1:2.5
Requires:	python-libxml2
Requires:	python-rpm
Requires:	python-sqlite
Requires:	python-urlgrabber
Requires:	rpm
Requires:	yum-metadata-parser
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Yum is a utility that can check for and automatically download and
install updated RPM packages. Dependencies are obtained and downloaded
automatically prompting the user as necessary.

%description -l pl.UTF-8
Yum to narzędzie sprawdzające i automatycznie ściągające i instalujące
uaktualnione pakiety RPM. Zależności są ściągane automatycznie po
zapytaniu użytkownika w razie potrzeby.

%package updatesd
Summary:	RPM update notifier daemon
Group:		Networking/Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	dbus
Requires:	python-dbus
Requires:	rc-scripts

%description updatesd
This is a daemon which periodically checks for updates and can send
notifications via mail, dbus or syslog.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d,yum/pluginconf.d},%{_libdir}/yum-plugins,%{_datadir}/yum-plugins}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum/repos.d/pld-source.repo
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/yum-updatesd

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post updatesd
/sbin/chkconfig --add yum-updatesd
%service yum-updatesd restart

%preun updatesd
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del yum-updatesd
	%service -q yum-updatesd stop
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS TODO INSTALL ChangeLog
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/yum.conf
%dir %{_sysconfdir}/yum
%dir %{_sysconfdir}/yum/repos.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/repos.d/*.repo
%dir %{_sysconfdir}/yum/pluginconf.d
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}

%attr(755,root,root) %{_bindir}/yum
%dir %{py_sitescriptdir}/yum
%dir %{py_sitescriptdir}/rpmUtils
%{_libdir}/yum-plugins
%{_datadir}/yum-plugins
%{py_sitescriptdir}/*/*.py[co]
%{_datadir}/yum-cli
/var/cache/yum
%{_mandir}/man*/*

%files updatesd
%defattr(644,root,root,755)
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/yum-updatesd.conf
/etc/dbus-1/system.d/yum-updatesd.conf
%attr(755,root,root) %{_sbindir}/yum-updatesd
%attr(754,root,root) /etc/rc.d/init.d/yum-updatesd
