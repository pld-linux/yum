Summary:	RPM installer/updater
Summary(pl):	Narzêdzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	2.2.2
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://www.linux.duke.edu/projects/yum/download/2.2/%{name}-%{version}.tar.gz
# Source0-md5:	734cc68e26c2fd07629616ab597acac6
#Source1:	yum.conf
#Source2:	yum.cron
Patch0:		%{name}-chroot.patch
URL:		http://www.linux.duke.edu/yum/
BuildRequires:	gettext-devel
BuildRequires:	python
BuildRequires:	rpmbuild(macros) >= 1.228
Requires:	rc-scripts
Requires(post,preun):	/sbin/chkconfig
Requires:	python
Requires:	python-libxml2
Requires:	python-rpm
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
%patch0 -p1

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..

# install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/etc/yum.conf
# install -m 755 %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.daily/yum.cron

#%find_lang %{name}

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
exit 0

%files
%defattr(644,root,root,755)
%doc README AUTHORS COPYING TODO INSTALL ChangeLog
%attr(755,root,root) %{_bindir}/yum
%attr(755,root,root) %{_bindir}/yum-arch
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.conf
%attr(755,root,root) /etc/cron.daily/yum.cron
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%dir %{py_sitescriptdir}/yum
%dir %{py_sitescriptdir}/repomd
%dir %{py_sitescriptdir}/rpmUtils
%dir %{py_sitescriptdir}/urlgrabber
%{py_sitescriptdir}/*/*.py[co]
%{_datadir}/yum-cli
/var/cache/yum
%{_mandir}/man*/*
