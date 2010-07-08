# TODO
# - PLDize (or drop) /etc/yum/version-groups.conf
Summary:	RPM installer/updater
Summary(pl.UTF-8):	Narzędzie do instalowania/uaktualniania pakietów RPM
Name:		yum
Version:	3.2.25
Release:	5
License:	GPL
Group:		Applications/System
BuildRequires:	rpmbuild(macros) >= 1.219
Source0:	http://yum.baseurl.org/download/3.2/%{name}-%{version}.tar.gz
# Source0-md5:	7fdea025aa8fb88376a283959d5d2d0f
Source1:	%{name}-pld-source.repo
Source2:	%{name}-pld-ti-source.repo
Patch1:		%{name}-obsoletes.patch
# from util-vserver-*/contrib/
Patch2:		%{name}-chroot.patch
Patch3:		%{name}-pld.patch
Patch4:		%{name}-amd64.patch
Patch5:		%{name}-config.patch
# fc
Patch10:	installonlyn-enable.patch
Patch11:	%{name}-mirror-priority.patch
Patch12:	%{name}-manpage-files.patch
Patch13:	%{name}-multilib-policy-best.patch
Patch14:	no-more-exactarchlist.patch
Patch16:	%{name}-HEAD.patch
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
Requires:	python-urlgrabber >= 1:3.9.1
Requires:	rpm >= 4.4.2
Requires:	yum-metadata-parser >= 1.1.4
BuildArch:	noarch
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_libdir		%{_prefix}/lib

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
# fc
%patch10 -p0
%patch11 -p0
%patch12 -p0
%patch13 -p0
%patch14 -p0
%patch16 -p1
# pld
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/{rc.d,sysconfig,yum/pluginconf.d},%{_libdir}/yum-plugins,%{_datadir}/yum-plugins}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PYLIBDIR=%{py_sitescriptdir}/..

# for now, move repodir/yum.conf back
mv $RPM_BUILD_ROOT%{_sysconfdir}/{yum/repos.d,/yum.repos.d}
mv $RPM_BUILD_ROOT%{_sysconfdir}/{yum/yum.conf,yum.conf}

cp -a %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/pld.repo

# change %{py_sitedir} to %{py_sitescriptdir} for 'noarch' packages!
%py_ocomp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli
%py_comp $RPM_BUILD_ROOT%{py_sitescriptdir} $RPM_BUILD_ROOT%{_datadir}/yum-cli

%py_postclean %{_datadir}/yum-cli

%find_lang %{name}

# in yum-updatesd.spec
rm $RPM_BUILD_ROOT/etc/dbus-1/system.d/yum-updatesd.conf
rm $RPM_BUILD_ROOT/etc/rc.d/init.d/yum-updatesd
rm $RPM_BUILD_ROOT%{_sysconfdir}/yum/yum-updatesd.conf
rm $RPM_BUILD_ROOT%{_sbindir}/yum-updatesd
rm $RPM_BUILD_ROOT%{_mandir}/man5/yum-updatesd.conf.5*
rm $RPM_BUILD_ROOT%{_mandir}/man8/yum-updatesd.8*

%clean
rm -rf $RPM_BUILD_ROOT

%pretrans
# migrate to new dir. having two dirs is really confusing
if [ -d %{_sysconfdir}/yum/repos.d ]; then
	echo >&2 "Migrating %{_sysconfdir}/yum/repos.d to %{_sysconfdir}/yum.repos.d"
	mkdir -p %{_sysconfdir}/yum.repos.d
	for a in %{_sysconfdir}/yum/repos.d/*; do
		if [ -f "$a" ]; then
			mv -vf $a %{_sysconfdir}/yum.repos.d/${a##*/}
		fi
	done
	rm -rf %{_sysconfdir}/yum/repos.d
fi

%triggerpostun -- %{name} < 3.2.12-3
if [ -f %{_sysconfdir}/yum/repos.d/pld-source.repo.rpmsave ]; then
	cp -f %{_sysconfdir}/yum/repos.d/pld.repo{,.rpmnew}
	mv -f %{_sysconfdir}/yum/repos.d/{pld-source.repo.rpmsave,pld.repo}
fi

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc README AUTHORS TODO INSTALL ChangeLog
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}

# main yum config
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.conf

%dir %{_sysconfdir}/yum
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum/version-groups.conf

%dir %{_sysconfdir}/yum.repos.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/yum.repos.d/*.repo

%dir %{_sysconfdir}/yum/pluginconf.d

%attr(755,root,root) %{_bindir}/yum

%dir %{py_sitescriptdir}/yum
%dir %{_datadir}/yum-cli
%{_datadir}/yum-cli/*.py[co]

%{py_sitescriptdir}/yum/*.py[co]
%dir %{py_sitescriptdir}/rpmUtils
%{py_sitescriptdir}/rpmUtils/*.py[co]

%dir %{_libdir}/yum-plugins
%dir %{_datadir}/yum-plugins

%{_mandir}/man5/yum.conf.5*
%{_mandir}/man8/yum-shell.8*
%{_mandir}/man8/yum.8*

/var/cache/yum

# bash-completion subpackage
/etc/bash_completion.d/yum.bash
