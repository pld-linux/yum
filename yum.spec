Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.2.0
Release:	3
License:	GPL
Group:		Applications/System
Source0:	http://linux.duke.edu/projects/yum/download/3.2/%{name}-%{version}.tar.gz
# Source0-md5:	535213fcdea6c3ea9a0839f9a2853492
Source1:	%{name}-pld-source.repo
Patch0:		%{name}-missingok.patch
URL:		http://linux.duke.edu/projects/yum/
BuildRequires:	gettext-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	python >= 2.5
Requires:	python-cElementTree
Requires:	python-libxml2
Requires:	python-rpm
Requires:	python-sqlite
Requires:	python-sqlite1
Requires:	python-urlgrabber
Requires:	rc-scripts
Requires:	rpm
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Yum is a utility that can check for and automatically download and
install updated RPM packages. Dependencies are obtained and downloaded
automatically prompting the user as necessary.

%description -l pl.UTF-8
Yum to narzędzie sprawdzające i automatycznie ściągające i instalujące
uaktualnione pakiety RPM. Zależności są ściągane automatycznie po
zapytaniu użytkownika w razie potrzeby.

%prep
%setup -q
%patch0 -p1

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d,yum/pluginconf.d},%{_libdir}/yum-plugins,%{_datadir}/yum-plugins}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum/repos.d/pld-source.repo

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add yum-updatesd
%service yum-updatesd restart

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del yum-updatesd
	%service -q yum-updatesd stop
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS TODO INSTALL ChangeLog
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/yum.conf
%dir %{_sysconfdir}/yum
%{_sysconfdir}/yum/repos.d
%dir %{_sysconfdir}/yum/pluginconf.d
%dir %{_sysconfdir}/dbus-1/system.d/yum-updatesd.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/yum-updatesd.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%attr(755,root,root) %{_bindir}/yum
%attr(755,root,root) %{_sbindir}/yum-updatesd
%attr(754,root,root) /etc/rc.d/init.d/yum-updatesd
%dir %{py_sitescriptdir}/yum
%dir %{py_sitescriptdir}/rpmUtils
%{_libdir}/yum-plugins
%{_datadir}/yum-plugins
%{py_sitescriptdir}/*/*.py[co]
%{_datadir}/yum-cli
/var/cache/yum
%{_mandir}/man*/*
