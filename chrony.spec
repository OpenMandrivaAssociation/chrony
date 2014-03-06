Name:		chrony
Version:	1.29
Release:	6
Summary:	An NTP client/server
Group:		System/Base
License:	GPLv2
URL:		http://chrony.tuxfamily.org
Source0:	http://download.tuxfamily.org/chrony/%{name}-%{version}.tar.gz
Source1:	chrony.conf
Source2:	chrony.keys
Source3:	chronyd.service
Source4:	chrony.helper
Source5:	chrony.logrotate
Source7:	chrony.nm-dispatcher
Source8:	chrony.dhclient
Source9:	chrony-wait.service
BuildRequires:	libcap-devel
BuildRequires:	libedit-devel
BuildRequires:	bison
BuildRequires:	texinfo
Requires(pre):	shadow-utils
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(postun):	rpm-helper
Requires(preun):	rpm-helper

%description
A client/server for the Network Time Protocol, this program keeps your
computer's clock accurate. It was specially designed to support
systems with intermittent internet connections, but it also works well
in permanently connected environments. It can use also hardware reference
clocks, system real-time clock or manual input as time references.

%prep
%setup -q

%build
%serverbuild
export CFLAGS="$CFLAGS -pie -fpie"
export LDFLAGS="$LDFLAGS -Wl,-z,relro,-z,now"

%configure \
        --docdir=%{_docdir} \
        --with-sendmail=%{_sbindir}/sendmail

%make getdate all docs

%install
%makeinstall_std install-docs

rm -rf %{buildroot}%{_docdir}

mkdir -p %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
mkdir -p %{buildroot}%{_localstatedir}/{lib,log}/chrony
mkdir -p %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d
mkdir -p %{buildroot}%{_sysconfdir}/dhcp/dhclient.d
mkdir -p %{buildroot}/usr/libexec/
mkdir -p %{buildroot}%{_unitdir}
mkdir -p %{buildroot}/lib/systemd/ntp-units.d

install -m 644 -p %{SOURCE1} %{buildroot}%{_sysconfdir}/chrony.conf
install -m 640 -p %{SOURCE2} %{buildroot}%{_sysconfdir}/chrony.keys
install -m 644 -p %{SOURCE3} %{buildroot}/lib/systemd/system/chronyd.service
install -m 755 -p %{SOURCE4} %{buildroot}/usr/libexec/chrony-helper
install -m 644 -p %{SOURCE5} %{buildroot}%{_sysconfdir}/logrotate.d/chrony
install -m 755 -p %{SOURCE7} %{buildroot}%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
install -m 755 -p %{SOURCE8} %{buildroot}%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
install -m 644 -p %{SOURCE9} %{buildroot}/lib/systemd/system/chrony-wait.service

touch %{buildroot}%{_localstatedir}/lib/chrony/{drift,rtc}
echo 'chronyd.service' > %{buildroot}/lib/systemd/ntp-units.d/50-chronyd.list

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /sbin/nologin

%post
%_post_service chronyd

%preun
%_preun_service chronyd

%postun
%_postun_userdel %{name}

%triggerun -- chrony < 1.25
if /sbin/chkconfig --level 3 chronyd; then
        /bin/systemctl enable chronyd.service &> /dev/null
fi
:

%files
%doc COPYING NEWS README chrony.txt faq.txt examples/*
%config(noreplace) %{_sysconfdir}/chrony.conf
%config(noreplace) %verify(not md5 size mtime) %attr(640,root,chrony) %{_sysconfdir}/chrony.keys
%config(noreplace) %{_sysconfdir}/logrotate.d/chrony
%{_sysconfdir}/NetworkManager/dispatcher.d/20-chrony
%{_sysconfdir}/dhcp/dhclient.d/chrony.sh
%{_bindir}/chronyc
%{_sbindir}/chronyd
/usr/libexec/chrony-helper
%{_infodir}/chrony.info*
/lib/systemd/ntp-units.d/*.list
%{_unitdir}/chrony*.service
%{_mandir}/man[158]/%{name}*.[158]*
%dir %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/drift
%ghost %attr(-,chrony,chrony) %{_localstatedir}/lib/chrony/rtc
%dir %attr(-,chrony,chrony) %{_localstatedir}/log/chrony

%changelog
* Thu Jan  3 2013 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.27-0.pre1git1ca844a.2
- drop dependency on 'info'

* Sat Nov 03 2012 Tomasz Pawel Gajc <tpg@mandriva.org> 1.27-0.pre1git1ca844a.1
+ Revision: 821779
- update to new version 1.27-pre1
- patch0: update to git b088b7
- update from fedora fils chrony.dhclient chrony-wait.service chrony.helper
- dont run info-install on %%post, %%preun
- spec file clean

* Sun Oct 09 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 1.26.20110831gitb088b7-2
+ Revision: 703948
- use global ntp servers in chrony.conf
- use %%serverbuild_hardened macro for mdv2012
- spec file clean

* Sun Sep 18 2011 Александр Казанцев <kazancas@mandriva.org> 1.26.20110831gitb088b7-1
+ Revision: 700224
- update to 1.26
- adapt for Mandriva use with systemd
- drop SysVinit service

* Wed May 04 2011 Michael Scherer <misc@mandriva.org> 1.25-1
+ Revision: 666398
- update to new version 1.25

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1.24-4mdv2011.0
+ Revision: 610138
- rebuild

* Thu Feb 25 2010 Oden Eriksson <oeriksson@mandriva.com> 1.24-3mdv2010.1
+ Revision: 511156
- bump release again...
- bump release due to unknown bs problems
- 1.24 (fixes CVE-2010-0292, CVE-2010-0293, CVE-2010-0294)
- rediffed one patch

* Thu Sep 10 2009 Thierry Vignaud <tv@mandriva.org> 1.23-8mdv2010.0
+ Revision: 437030
- rebuild

* Fri Apr 03 2009 Funda Wang <fwang@mandriva.org> 1.23-7mdv2009.1
+ Revision: 363669
- rebuild for new readline

* Thu Mar 26 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.23-6mdv2009.1
+ Revision: 361432
- rebuild

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - rebuild for latest readline

* Wed Jul 23 2008 Thierry Vignaud <tv@mandriva.org> 1.23-3mdv2009.0
+ Revision: 243883
- rebuild

* Mon Jan 28 2008 Adam Williamson <awilliamson@mandriva.org> 1.23-1mdv2008.1
+ Revision: 159227
- buildrequires texinfo (for .info file creation)
- new release 1.23 (hopefully fix #23977)
- rewrap description
- new license policy
- spec clean

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - import chrony


* Wed Jun 21 2006 Lenny Cartier <lenny@mandriva.com> 1.22-0.20060621mdv2007.0
- conflicts ntp openntpd
- update to 20060621

* Sun Apr 03 2005 Michael Scherer <misc@mandrake.org> 1.20-3mdk
- Rebuild for readline

* Fri Jan 03 2004 Franck Villaume <fvill@freesurf.fr> 1.20-2mdk
- add BuildRequires : readline-devel

* Sun Dec 14 2003 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.20-1mdk
- 1.20
- cleanups
- macroize
- quiet setup
- rm -rf $RPM_BUILD_ROOT in %%install, not %%prep
- fix buildrequires (lib64..)
- add clean section
- fix init script (P1) in stead of messing with symlinks for chkconfig
- compile with $RPM_OPT_FLAGS

* Mon Apr 28 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.19-2mdk
- adjust buildrequires

* Wed Jan 22 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.19-1mdk
- from Aleksander Adamowski <olo@altkom.com.pl> :
	- update to version 1.19
- add manpages

* Fri Sep 20 2002 Aleksander Adamowski <olo@altkom.com.pl> 1.18-1mdk
	- update to version 1.18

* Wed Jul 24 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.17-3mdk
- rebuild for new readline

* Mon May 27 2002 Lenny Cartier <lenny@mandrakesoft.com> 1.17-2mdk
- fixed by Vlatko Kosturjak <kost@linux-mandrake.com> :
	- fix for /etc/init.d/chronyd script (missing quote)
	- fix for info install/uninstall
	- support for chkconfig (chronyd is now visible in drakxservices)

* Thu Mar 07 2002  Lenny Cartier <lenny@mandrakesoft.com> 1.17-1mdk
- updated by W. Unruh <unruh@physics.ubc.ca> :
	- update to version 1.17

* Thu Jun 15 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.15-1mdk
- update to 1.15

* Fri Jan 05 2001 David BAUDENS <baudens@mandrakesoft.com> 1.14-3mdk
- ExcludeArch: ppc
- Macros
- Spec clean up

* Wed Sep 27 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.14-2mdk
- fix info pages

* Mon Sep 25 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.14-1mdk
- include fixes from :
 	Tue Sep 18 2000 W. Unruh <unruh@phsyics.ubc.ca> 1.14-1mdk
	-fix links in /etc/rc.d
	-update to version 1.14
- macros

* Tue Apr 25 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.11-2mdk
- fix group
- spec helper fixes

* Mon Feb 07 2000 Lenny Cartier <lenny@mandrakesoft.com>
- fixed non-root build of the package
- bypass install script
- add correct links
- used original srpm provided by Per Wedin <perra@m-media.se>

* Sun Feb 06 2000 Per Wedin <perra@m-media.se>
- 1.11-2: Minor changes in chrony-1.11.spec
 
* Sat Feb 05 2000 Per Wedin <perra@m-media.se>
- New version: 1.11-1. First try...
 
* Wed Jun 24 1998 Corey Minyard <minyard@acm.org>
- Fixed all the configuration information so it went out correctly
 
* Mon Jun 22 1998 Corey Minyard <minyard@acm.org>
- Initial version.
* Sun Oct 09 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 1.26.20110831gitb088b7-2mdv2012.0
+ Revision: 703948
- use global ntp servers in chrony.conf
  > - use %%serverbuild_hardened macro for mdv2012^C
- spec file clean

* Sun Sep 18 2011 ÐÐ»ÐµÐºÑÐ°Ð½Ð´Ñ ÐÐ°Ð·Ð°Ð½ÑÐµÐ² <kazancas@mandriva.org> 1.26.20110831gitb088b7-1
+ Revision: 700224
- update to 1.26
- adapt for Mandriva use with systemd
- drop SysVinit service

* Wed May 04 2011 Michael Scherer <misc@mandriva.org> 1.25-1
+ Revision: 666398
- update to new version 1.25

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1.24-4mdv2011.0
+ Revision: 610138
- rebuild

* Thu Feb 25 2010 Oden Eriksson <oeriksson@mandriva.com> 1.24-3mdv2010.1
+ Revision: 511156
- bump release again...
- bump release due to unknown bs problems
- 1.24 (fixes CVE-2010-0292, CVE-2010-0293, CVE-2010-0294)
- rediffed one patch

* Thu Sep 10 2009 Thierry Vignaud <tv@mandriva.org> 1.23-8mdv2010.0
+ Revision: 437030
- rebuild

* Fri Apr 03 2009 Funda Wang <fwang@mandriva.org> 1.23-7mdv2009.1
+ Revision: 363669
- rebuild for new readline

* Thu Mar 26 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1.23-6mdv2009.1
+ Revision: 361432
- rebuild

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - rebuild for latest readline

* Wed Jul 23 2008 Thierry Vignaud <tv@mandriva.org> 1.23-3mdv2009.0
+ Revision: 243883
- rebuild

* Mon Jan 28 2008 Adam Williamson <awilliamson@mandriva.org> 1.23-1mdv2008.1
+ Revision: 159227
- buildrequires texinfo (for .info file creation)
- new release 1.23 (hopefully fix #23977)
- rewrap description
- new license policy
- spec clean

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - import chrony


* Wed Jun 21 2006 Lenny Cartier <lenny@mandriva.com> 1.22-0.20060621mdv2007.0
- conflicts ntp openntpd
- update to 20060621

* Sun Apr 03 2005 Michael Scherer <misc@mandrake.org> 1.20-3mdk
- Rebuild for readline

* Fri Jan 03 2004 Franck Villaume <fvill@freesurf.fr> 1.20-2mdk
- add BuildRequires : readline-devel

* Sun Dec 14 2003 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 1.20-1mdk
- 1.20
- cleanups
- macroize
- quiet setup
- rm -rf $RPM_BUILD_ROOT in %%install, not %%prep
- fix buildrequires (lib64..)
- add clean section
- fix init script (P1) in stead of messing with symlinks for chkconfig
- compile with $RPM_OPT_FLAGS

* Mon Apr 28 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.19-2mdk
- adjust buildrequires

* Wed Jan 22 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.19-1mdk
- from Aleksander Adamowski <olo@altkom.com.pl> :
	- update to version 1.19
- add manpages

* Fri Sep 20 2002 Aleksander Adamowski <olo@altkom.com.pl> 1.18-1mdk
	- update to version 1.18

* Wed Jul 24 2002 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.17-3mdk
- rebuild for new readline

* Mon May 27 2002 Lenny Cartier <lenny@mandrakesoft.com> 1.17-2mdk
- fixed by Vlatko Kosturjak <kost@linux-mandrake.com> :
	- fix for /etc/init.d/chronyd script (missing quote)
	- fix for info install/uninstall
	- support for chkconfig (chronyd is now visible in drakxservices)

* Thu Mar 07 2002  Lenny Cartier <lenny@mandrakesoft.com> 1.17-1mdk
- updated by W. Unruh <unruh@physics.ubc.ca> :
	- update to version 1.17

* Thu Jun 15 2001 Lenny Cartier <lenny@mandrakesoft.com> 1.15-1mdk
- update to 1.15

* Fri Jan 05 2001 David BAUDENS <baudens@mandrakesoft.com> 1.14-3mdk
- ExcludeArch: ppc
- Macros
- Spec clean up

* Wed Sep 27 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.14-2mdk
- fix info pages

* Mon Sep 25 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.14-1mdk
- include fixes from :
 	Tue Sep 18 2000 W. Unruh <unruh@phsyics.ubc.ca> 1.14-1mdk
	-fix links in /etc/rc.d
	-update to version 1.14
- macros

* Tue Apr 25 2000 Lenny Cartier <lenny@mandrakesoft.com> 1.11-2mdk
- fix group
- spec helper fixes

* Mon Feb 07 2000 Lenny Cartier <lenny@mandrakesoft.com>
- fixed non-root build of the package
- bypass install script
- add correct links
- used original srpm provided by Per Wedin <perra@m-media.se>

* Sun Feb 06 2000 Per Wedin <perra@m-media.se>
- 1.11-2: Minor changes in chrony-1.11.spec
 
* Sat Feb 05 2000 Per Wedin <perra@m-media.se>
- New version: 1.11-1. First try...
 
* Wed Jun 24 1998 Corey Minyard <minyard@acm.org>
- Fixed all the configuration information so it went out correctly
 
* Mon Jun 22 1998 Corey Minyard <minyard@acm.org>
- Initial version.
