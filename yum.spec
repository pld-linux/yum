Summary:	RPM installer/updater
Name:		yum
Version:	2.0.7
Release:	1
License:	GPL
Group:		Applications/System
Source0:	http://www.linux.duke.edu/projects/yum/download/2.0/%{name}-%{version}.tar.gz
#Source1: yum.conf
#Source2: yum.cron
URL:		http://www.linux.duke.edu/yum/
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
BuildArch:	noarch
BuildRequires:	python
BuildRequires:	gettext
Requires:	python, rpm-python, rpm libxml2-python
Prereq:		/sbin/chkconfig, /sbin/service

%description
Yum is a utility that can check for and automatically download and
install updated RPM packages. Dependencies are obtained and downloaded
automatically prompting the user as necessary.

%prep
%setup -q

%build
%configure
%{__make}


%install
rm -rf $RPM_BUILD_ROOT
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
%{__make} DESTDIR=$RPM_BUILD_ROOT install
# install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/etc/yum.conf
# install -m 755 %{SOURCE2} $RPM_BUILD_ROOT/etc/cron.daily/yum.cron

%find_lang %{name}

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add yum
#/sbin/chkconfig yum on
#/sbin/service yum condrestart >> /dev/null
#exit 0


%preun
if [ $1 = 0 ]; then
	/sbin/chkconfig --del yum
	/etc/rc.d/init.d/yum stop
fi
exit 0

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README AUTHORS COPYING TODO INSTALL ChangeLog
%config(noreplace) %{_sysconfdir}/yum.conf
%config(noreplace) %{_sysconfdir}/cron.daily/yum.cron
%config %{_sysconfdir}/init.d/%{name}
%config %{_sysconfdir}/logrotate.d/%{name}
%{_datadir}/yum/*
%attr(755,root,root) %{_bindir}/yum
%attr(755,root,root) %{_bindir}/yum-arch
/var/cache/yum
%{_mandir}/man*/*
