Summary:	RPM installer/updater
Summary(pl):	Narzêdzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	2.6.1
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://linux.duke.edu/projects/yum/download/2.6/%{name}-%{version}.tar.gz
# Source0-md5:	2dc94410341ef7f4171a7ecdc00be5bf
Patch0:		%{name}-chroot.patch
URL:		http://linux.duke.edu/projects/yum/
BuildRequires:	gettext-devel
BuildRequires:	rpm-pythonprov
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
Requires:	python
Requires:	python-cElementTree >= 1.0.5
Requires:	python-libxml2
Requires:	python-rpm
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

%description -l pl
Yum to narzêdzie sprawdzaj±ce i automatycznie ¶ci±gaj±ce i instaluj±ce
uaktualnione pakiety RPM. Zale¿no¶ci s± ¶ci±gane automatycznie po
zapytaniu u¿ytkownika w razie potrzeby.

%prep
%setup -q
#%patch0 -p1 CHECKME

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..

%py_postclean

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add yum
%service yum restart

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del yum
	%service -q yum stop
fi

%files
%defattr(644,root,root,755)
%doc README AUTHORS COPYING TODO INSTALL ChangeLog
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.conf
%dir %{_sysconfdir}/yum
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/yum-daily.yum
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%attr(755,root,root) %{_bindir}/yum
%attr(755,root,root) %{_bindir}/yum-arch
%attr(755,root,root) /etc/cron.daily/yum.cron
%attr(755,root,root) /etc/cron.weekly/yum.cron
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{py_sitescriptdir}/yum
%dir %{py_sitescriptdir}/repomd
%dir %{py_sitescriptdir}/rpmUtils
%{py_sitescriptdir}/*/*.py[co]
%{_datadir}/yum-cli
/var/cache/yum
%{_mandir}/man*/*
