%define	name	chrony
%define	version	1.22
%define cvsver 20060621
%define	release %mkrel 0.%{cvsver}

Summary:	Chrony clock synchronization program
Name:		%{name}
Version:	%{version}
Release:	%{release}
Url:		http://chrony.sunsite.dk/index.php
License:	GPL
Group:		System/Configuration/Other
Source0:	%{name}-%{version}.%{cvsver}.tar.bz2
Patch0:		%{name}-1.19-fix.patch.bz2
Patch1:		%{name}-1.20-fix-chkconfig.patch.bz2
Buildrequires:	termcap-devel ncurses-devel readline-devel
Requires(pre):	rpm-helper
Conflicts:	ntp openntpd

%description
A pair of programs for keeping computer clocks accurate.
chronyd is a background (daemon) program and chronyc is a
command-line interface to it.  Time reference sources for
chronyd can be RFC1305 NTP servers, human (via keyboard and
chronyc), and the computer's real-time clock at boot time
(Linux only).  chronyd can determine the rate at which the
computer gains or loses time and compensate for it whilst no
external reference is present.  chronyd's use of NTP servers
can be switched on and off (through chronyc) to support
computers with dial-up/intermittent access to the
Internet. chronyd can also act as an RFC1305-compatible NTP
server.

%prep
%setup -q -n %{name}-%{version}.%{cvsver}
%patch0 -p1
%patch1 -p1

%build
CFLAGS="$RPM_OPT_FLAGS" \
./configure --prefix=%{_prefix}
%make
%make info

%install
rm -rf $RPM_BUILD_ROOT
install -m755 -d  $RPM_BUILD_ROOT/var/log/chrony

install -m755 chronyd.init -D $RPM_BUILD_ROOT%{_initrddir}/chronyd
install -m644 chrony.conf -D $RPM_BUILD_ROOT%{_sysconfdir}/chrony.conf
install -m644 chrony.keys -D $RPM_BUILD_ROOT%{_sysconfdir}/chrony.keys
install -m644 chrony.log -D $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/chrony

#make install

install -m755 -d $RPM_BUILD_ROOT%{_bindir}
install -m755 -d $RPM_BUILD_ROOT%{_sbindir} 
install -m755 chronyd $RPM_BUILD_ROOT%{_sbindir}
install -m755 chronyc $RPM_BUILD_ROOT%{_bindir}

install -m755 -d $RPM_BUILD_ROOT%{_mandir}/man1
install -m755 -d $RPM_BUILD_ROOT%{_mandir}/man8
install -m644 chrony.1 $RPM_BUILD_ROOT%{_mandir}/man1
install -m644 chronyc.1 $RPM_BUILD_ROOT%{_mandir}/man1
install -m644 chronyd.8 $RPM_BUILD_ROOT%{_mandir}/man8

install -m755 -d %buildroot/%_infodir
install -m644 chrony.info %buildroot/%_infodir

%post 
%_install_info chrony.info
%_post_service chronyd

%postun
rm -f %{_sysconfdir}/chrony.drift %{_sysconfdir}/chrony.rtc

%preun
%_remove_install_info chrony.info
%_preun_service chronyd

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr (-,root,root)
%{_sbindir}/*
%{_bindir}/*
%dir /var/log/chrony
%config(noreplace) %{_initrddir}/chronyd
%config(noreplace) %{_sysconfdir}/chrony.conf
%config(noreplace) %{_sysconfdir}/chrony.keys
%config(noreplace) %{_sysconfdir}/logrotate.d/chrony
%doc INSTALL README README.rh COPYING chrony.texi
%{_infodir}/chrony.info*
%{_mandir}/man1/*
%{_mandir}/man8/*

