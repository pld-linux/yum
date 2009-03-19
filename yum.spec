Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.2.21
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://yum.baseurl.org/download/3.2/%{name}-%{version}.tar.gz
# Source0-md5:	2c9ff2e3c329e5cd0ce335d05bf96b7b
Source1:	%{name}-pld-source.repo
Source2:	%{name}-pld-ti-source.repo
Source3:	%{name}-updatesd.init
Source4:	%{name}-updatesd.sysconfig
Patch1:		%{name}-obsoletes.patch
# from util-vserver-*/contrib/
Patch2:		%{name}-chroot.patch
URL:		http://yum.baseurl.org/
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
Requires:	python >= 1:2.5
Requires:	python-iniparse
Requires:	python-libxml2
Requires:	python-pygpgme
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
Summary(pl.UTF-8):	Demon powiadamiający o uaktualnionych RPM-ach
Group:		Networking/Daemons
Requires(post,preun):	/sbin/chkconfig
Requires:	%{name} = %{version}-%{release}
Requires:	dbus
Requires:	python-dbus
Requires:	rc-scripts

%description updatesd
This is a daemon which periodically checks for updates and can send
notifications via mail, dbus or syslog.

%description updatesd -l pl.UTF-8
Ten pakiet zawiera demona regularnie sprawdzającego dostępność
uaktualnień, mogącego wysyłać uaktualnienia pocztą elektroniczną,
poprzez dbus lub sysloga.

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d,sysconfig,yum/pluginconf.d},%{_libdir}/yum-plugins,%{_datadir}/yum-plugins}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..

%ifarch i486 i686 ppc sparc alpha athlon
%define		_ftp_arch	%{_target_cpu}
%endif
%ifarch %{x8664}
%define		_ftp_arch	x86_64
%endif
%ifarch i586
%if "%{pld_release}" == "ti"
%define		_ftp_arch	i586
%else
%define		_ftp_arch	i486
%endif
%endif
%ifarch pentium2 pentium3 pentium4
%define		_ftp_arch	i686
%endif
%ifarch sparcv9 sparc64
%define		_ftp_arch	sparc
%endif

%if "%{pld_release}" == "ti"
sed -e '
    s|%%ARCH%%|%{_ftp_arch}|g
    ' < %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/yum/repos.d/pld.repo
%else
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum/repos.d/pld.repo
%endif
install %{SOURCE3} $RPM_BUILD_ROOT/etc/rc.d/init.d/yum-updatesd
install %{SOURCE4} $RPM_BUILD_ROOT/etc/sysconfig/yum-updatesd

%py_postclean

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pretrans
# migrate to new dir. having two dirs is really confusing
if [ -d %{_sysconfdir}/yum.repos.d ]; then
	echo >&2 "Migrating %{_sysconfdir}/yum.repos.d to %{_sysconfdir}/yum/repos.d"
	mkdir -p %{_sysconfdir}/yum/repos.d
	for a in %{_sysconfdir}/yum.repos.d/*; do
		if [ -f "$a" ]; then
			mv -vf $a %{_sysconfdir}/yum/repos.d/${a##*/}
		fi
	done
	rm -rf %{_sysconfdir}/yum.repos.d
fi

%post updatesd
/sbin/chkconfig --add yum-updatesd
%service yum-updatesd restart

%preun updatesd
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del yum-updatesd
	%service -q yum-updatesd stop
fi

%triggerpostun -- %{name} < 3.2.12-3
if [ -f %{_sysconfdir}/yum/repos.d/pld-source.repo.rpmsave ]; then
	cp -f %{_sysconfdir}/yum/repos.d/pld.repo{,.rpmnew}
	mv -f %{_sysconfdir}/yum/repos.d/{pld-source.repo.rpmsave,pld.repo}
fi

%files -f %{name}.lang
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
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/yum-updatesd
%attr(754,root,root) /etc/rc.d/init.d/yum-updatesd
