Summary:	RPM installer/updater
Summary(pl):	Narzêdzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	2.0.7
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://www.linux.duke.edu/projects/yum/download/2.0/%{name}-%{version}.tar.gz
#Source1:	yum.conf
#Source2:	yum.cron
URL:		http://www.linux.duke.edu/yum/
BuildRequires:	gettext-devel
BuildRequires:	python
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

%build
%configure
%{__make}


%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/etc/rc.d

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT
# install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/etc/yum.conf
# install -m 755 %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.daily/yum.cron
mv $RPM_BUILD_ROOT/etc/init.d $RPM_BUILD_ROOT/etc/rc.d/

%find_lang %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add yum
#/etc/rc.d/init.d/yum condrestart >> /dev/null

%preun
if [ "$1" = "0" ]; then
	/sbin/chkconfig --del yum
# XXX: check if running
	/etc/rc.d/init.d/yum stop
fi
exit 0

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README AUTHORS COPYING TODO INSTALL ChangeLog
%attr(755,root,root) %{_bindir}/yum
%attr(755,root,root) %{_bindir}/yum-arch
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/yum.conf
%config(noreplace) %verify(not size mtime md5) /etc/cron.daily/yum.cron
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%config(noreplace) %verify(not size mtime md5) /etc/logrotate.d/%{name}
%{_datadir}/yum
/var/cache/yum
%{_mandir}/man*/*
