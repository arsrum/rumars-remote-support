import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:url_launcher/url_launcher.dart';

class RumarsBrandingPanel extends StatelessWidget {
  const RumarsBrandingPanel({super.key});
  static const supportPhone = '+375 (29) 743-01-51';
  static const supportUrl = 'https://rumars.pro';

  Future<void> _openWebsite() async {
    await launchUrl(Uri.parse(supportUrl), mode: LaunchMode.externalApplication);
  }

  Future<void> _copyPhone() async {
    await Clipboard.setData(const ClipboardData(text: supportPhone));
  }

  @override
  Widget build(BuildContext context) {
    final muted = Theme.of(context).colorScheme.onSurface.withOpacity(0.65);
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 10, 8, 12),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Image.asset('assets/rumars_logo.png', width: 112, height: 112),
          const SizedBox(height: 4),
          Text('RUMARS SOLUTION',
            textAlign: TextAlign.center,
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12,
              color: Theme.of(context).colorScheme.onSurface)),
          Text('REMOTE SUPPORT',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 10, letterSpacing: 0.7, color: muted)),
          const SizedBox(height: 10),
          Text('Техническая поддержка',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: muted)),
          Tooltip(
            message: 'Нажмите, чтобы скопировать номер',
            child: InkWell(
              onTap: _copyPhone,
              child: const Padding(
                padding: EdgeInsets.symmetric(vertical: 4),
                child: Text(supportPhone,
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
              ),
            ),
          ),
          InkWell(
            onTap: _openWebsite,
            child: const Padding(
              padding: EdgeInsets.symmetric(vertical: 3),
              child: Text('rumars.pro',
                textAlign: TextAlign.center,
                style: TextStyle(color: Color(0xFF177BC0),
                  fontSize: 12, decoration: TextDecoration.underline)),
            ),
          ),
        ],
      ),
    );
  }
}